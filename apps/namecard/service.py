# -*- encoding: utf-8 -*-

import base64
import json
import os
import re
import uuid
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import cv2  # type: ignore
import numpy as np  # type: ignore


@dataclass
class SegmentedCard:
    filename: str
    width: int
    height: int
    bbox: Tuple[int, int, int, int]  # x, y, w, h on original image


class NameCardProcessor:
    """
    Segmentation-first pipeline:
    - read a multi-card image
    - detect card-like rectangles
    - crop/deskew each card
    - save crops as files
    """

    def __init__(self, job_dir: str, debug: bool = False):
        self.job_dir = job_dir
        self.crops_dir = os.path.join(job_dir, "crops")
        os.makedirs(self.crops_dir, exist_ok=True)
        self.debug = bool(debug)
        self.debug_dir = os.path.join(job_dir, "debug")
        if self.debug:
            os.makedirs(self.debug_dir, exist_ok=True)

    def segment_and_save(self, input_image_path: str) -> List[SegmentedCard]:
        img = cv2.imread(input_image_path)
        if img is None:
            raise ValueError(f"Failed to read image: {input_image_path}")

        h, w = img.shape[:2]
        if self.debug:
            print(f"[NameCardProcessor] input={input_image_path} size={w}x{h}")
            self._write_debug_image("00_original.jpg", img)

        boxes = self._detect_candidate_boxes(img)
        if self.debug:
            print(f"[NameCardProcessor] detected_boxes={len(boxes)}")
            overlay = img.copy()
            for i, q in enumerate(boxes, start=1):
                pts = self._order_quad(np.array(q))
                pts_int = np.array(pts, dtype=np.int32).reshape((-1, 1, 2))
                cv2.polylines(overlay, [pts_int], True, (0, 255, 0), 3)
                x, y, bw, bh = self._quad_bbox(q)
                cv2.putText(overlay, str(i), (x, max(0, y - 10)), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)
            self._write_debug_image("04_boxes_overlay.jpg", overlay)

        # Fallback: treat as a single card.
        if not boxes:
            filename = "card_001.jpg"
            out_path = os.path.join(self.crops_dir, filename)
            cv2.imwrite(out_path, img)
            return [SegmentedCard(filename=filename, width=w, height=h, bbox=(0, 0, w, h))]

        cards: List[SegmentedCard] = []
        for idx, quad in enumerate(boxes, start=1):
            crop = self._warp_quad(img, quad)
            if crop is None or crop.size == 0:
                continue
            ch, cw = crop.shape[:2]
            filename = f"card_{idx:03d}.jpg"
            out_path = os.path.join(self.crops_dir, filename)
            cv2.imwrite(out_path, crop)
            x, y, bw, bh = self._quad_bbox(quad)
            cards.append(SegmentedCard(filename=filename, width=cw, height=ch, bbox=(x, y, bw, bh)))

        # Fallback if everything failed to warp/save
        if not cards:
            filename = "card_001.jpg"
            out_path = os.path.join(self.crops_dir, filename)
            cv2.imwrite(out_path, img)
            return [SegmentedCard(filename=filename, width=w, height=h, bbox=(0, 0, w, h))]

        return cards

    def _detect_candidate_boxes(self, img) -> List[Any]:
        """
        Returns list of 4-point quads (float32) in original image coordinates.
        """
        h, w = img.shape[:2]
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (5, 5), 0)

        # Heuristics: business cards can be relatively small in a multi-card photo.
        min_area = max(0.005 * (w * h), 5_000)

        debug_info = {"image": {"w": w, "h": h}, "min_area": min_area, "candidates": []}

        def accept_rect(rect, source: str):
            (cx, cy), (rw, rh), angle = rect
            if rw <= 0 or rh <= 0:
                return None
            ar = max(rw, rh) / (min(rw, rh) + 1e-6)
            # business cards are often ~1.5-2.2 aspect ratio; allow wider bounds.
            if ar < 1.1 or ar > 5.0:
                return None
            box = cv2.boxPoints(rect)  # 4 points
            area = float(rw * rh)
            debug_info["candidates"].append(
                {
                    "source": source,
                    "center": [float(cx), float(cy)],
                    "size": [float(rw), float(rh)],
                    "angle": float(angle),
                    "aspect_ratio": float(ar),
                    "area_est": float(area),
                    "bbox": list(self._quad_bbox(box)),
                }
            )
            return box

        quads: List[Any] = []

        # Pipeline A: Edge detection + morphology to connect card borders
        edges = cv2.Canny(gray, 40, 140)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (7, 7))
        edges = cv2.dilate(edges, kernel, iterations=2)
        edges = cv2.erode(edges, kernel, iterations=1)
        if self.debug:
            self._write_debug_image("01_edges.jpg", edges)

        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if self.debug:
            print(f"[NameCardProcessor] edge_contours={len(contours)}")

        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area < min_area:
                continue
            rect = cv2.minAreaRect(cnt)
            box = accept_rect(rect, "edges")
            if box is not None:
                quads.append(box)

        # Pipeline B (fallback/augment): Adaptive threshold + morphology (better for low-contrast edges)
        # Cards are mostly light rectangles on a darker background: use inverse threshold.
        thr = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 31, 7
        )
        if self.debug:
            self._write_debug_image("02_thresh.jpg", thr)

        # Close small gaps; then open to remove specks
        k_close = cv2.getStructuringElement(cv2.MORPH_RECT, (11, 11))
        k_open = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        morph = cv2.morphologyEx(thr, cv2.MORPH_CLOSE, k_close, iterations=2)
        morph = cv2.morphologyEx(morph, cv2.MORPH_OPEN, k_open, iterations=1)
        if self.debug:
            self._write_debug_image("03_morph.jpg", morph)

        contours2, _ = cv2.findContours(morph, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if self.debug:
            print(f"[NameCardProcessor] thresh_contours={len(contours2)}")

        for cnt in contours2:
            area = cv2.contourArea(cnt)
            if area < min_area:
                continue
            rect = cv2.minAreaRect(cnt)
            box = accept_rect(rect, "thresh")
            if box is not None:
                quads.append(box)

        # Sort quads top-to-bottom then left-to-right
        def sort_key(q):
            x, y, bw, bh = self._quad_bbox(q)
            return (y, x)

        quads.sort(key=sort_key)

        # Remove near-duplicates (same location/size)
        deduped: List[Any] = []
        for q in quads:
            x, y, bw, bh = self._quad_bbox(q)
            too_close = False
            for oq in deduped:
                ox, oy, obw, obh = self._quad_bbox(oq)
                if abs(x - ox) < 20 and abs(y - oy) < 20 and abs(bw - obw) < 40 and abs(bh - obh) < 40:
                    too_close = True
                    break
            if not too_close:
                deduped.append(q)

        if self.debug:
            debug_info["deduped"] = len(deduped)
            with open(os.path.join(self.debug_dir, "boxes.json"), "w", encoding="utf-8") as f:
                json.dump(debug_info, f, ensure_ascii=False, indent=2)

        return deduped

    def _order_quad(self, pts):
        # pts: 4x2
        pts = pts.astype("float32")
        s = pts.sum(axis=1)
        diff = (pts[:, 0] - pts[:, 1])
        tl = pts[s.argmin()]
        br = pts[s.argmax()]
        tr = pts[diff.argmax()]
        bl = pts[diff.argmin()]
        return [tl, tr, br, bl]

    def _warp_quad(self, img, quad):
        # Expand slightly to avoid clipping due to small rotation/inaccurate contour.
        quad = self._expand_quad(np.array(quad, dtype="float32"), img.shape[1], img.shape[0], scale=1.03)
        pts = self._order_quad(quad)
        (tl, tr, br, bl) = pts

        widthA = ((br[0] - bl[0]) ** 2 + (br[1] - bl[1]) ** 2) ** 0.5
        widthB = ((tr[0] - tl[0]) ** 2 + (tr[1] - tl[1]) ** 2) ** 0.5
        maxW = int(max(widthA, widthB))

        heightA = ((tr[0] - br[0]) ** 2 + (tr[1] - br[1]) ** 2) ** 0.5
        heightB = ((tl[0] - bl[0]) ** 2 + (tl[1] - bl[1]) ** 2) ** 0.5
        maxH = int(max(heightA, heightB))

        if maxW < 80 or maxH < 80:
            return None

        dst = np.array([[0, 0], [maxW - 1, 0], [maxW - 1, maxH - 1], [0, maxH - 1]], dtype="float32")
        M = cv2.getPerspectiveTransform(np.array(pts, dtype="float32"), dst)
        warped = cv2.warpPerspective(img, M, (maxW, maxH))

        # Rotate to landscape if needed
        wh = warped.shape[:2]
        if wh[0] > wh[1] * 1.1:
            # portrait -> rotate 90deg
            warped = cv2.rotate(warped, cv2.ROTATE_90_CLOCKWISE)

        return warped

    def _expand_quad(self, quad: np.ndarray, img_w: int, img_h: int, scale: float = 1.02) -> np.ndarray:
        """
        Expand quad points outward around their centroid by a scale factor, then clip to image bounds.
        """
        if quad.shape[0] != 4:
            return quad
        c = quad.mean(axis=0)
        expanded = (quad - c) * float(scale) + c
        expanded[:, 0] = np.clip(expanded[:, 0], 0, img_w - 1)
        expanded[:, 1] = np.clip(expanded[:, 1], 0, img_h - 1)
        return expanded

    def _write_debug_image(self, name: str, img) -> None:
        if not self.debug:
            return
        path = os.path.join(self.debug_dir, name)
        try:
            cv2.imwrite(path, img)
        except Exception as e:
            print(f"[NameCardProcessor] failed to write debug image {path}: {e}")

    def _quad_bbox(self, quad) -> Tuple[int, int, int, int]:
        xs = [p[0] for p in quad]
        ys = [p[1] for p in quad]
        x1, x2 = int(min(xs)), int(max(xs))
        y1, y2 = int(min(ys)), int(max(ys))
        return x1, y1, max(1, x2 - x1), max(1, y2 - y1)


class OpenAIBusinessCardExtractor:
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model or os.getenv("OPENAI_VISION_MODEL", "gpt-4o-mini")

        if not self.api_key:
            raise ValueError("OPENAI_API_KEY is not set")

        # Lazy import so app can start without OpenAI in some contexts.
        from openai import OpenAI  # type: ignore

        self.client = OpenAI(api_key=self.api_key)

    def extract_fields(self, image_path: str) -> Dict[str, Any]:
        """
        Returns normalized fields. This does NOT write to DB.
        """
        with open(image_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode("utf-8")

        schema = {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "name": {"type": ["string", "null"]},
                "job_title": {"type": ["string", "null"]},
                "email": {"type": ["string", "null"]},
                "phone": {"type": ["string", "null"]},
                "mobile": {"type": ["string", "null"]},
                "company_name": {"type": ["string", "null"]},
                "company_phone": {"type": ["string", "null"]},
                "address": {"type": ["string", "null"]},
                "website": {"type": ["string", "null"]},
                "raw_text": {"type": ["string", "null"]},
                "notes": {"type": ["string", "null"]},
            },
            "required": ["name", "job_title", "email", "phone", "mobile", "company_name", "company_phone", "address", "website", "raw_text", "notes"],
        }

        prompt = (
            "You are extracting contact info from a business card image. "
            "Return JSON that matches the provided schema. "
            "If a field is unknown, return null. "
            "Prefer mobile for personal cellphone; phone for office/landline; company_phone for company main line."
        )

        resp = self.client.responses.create(
            model=self.model,
            input=[
                {
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text": prompt},
                        {"type": "input_image", "image_url": f"data:image/jpeg;base64,{b64}"},
                    ],
                }
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {"name": "business_card", "schema": schema, "strict": True},
            },
        )

        # openai Responses API: output_text is convenient but we want the JSON object.
        text = getattr(resp, "output_text", None)
        if not text:
            # best-effort fallback: stringify whole response
            text = str(resp)

        try:
            data = json.loads(text)
        except Exception:
            data = {"raw_text": text}

        return self._normalize(data)

    def _normalize(self, data: Dict[str, Any]) -> Dict[str, Any]:
        def clean_str(v):
            if v is None:
                return None
            v = str(v).strip()
            return v if v else None

        out = {k: clean_str(data.get(k)) for k in [
            "name", "job_title", "email", "phone", "mobile", "company_name",
            "company_phone", "address", "website", "raw_text", "notes"
        ]}

        # basic email normalization
        if out["email"]:
            m = re.search(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", out["email"], flags=re.I)
            out["email"] = m.group(0) if m else out["email"]

        # basic phone normalization: keep digits/+/#/()/-/space
        def clean_phone(p):
            if not p:
                return None
            p = re.sub(r"[^0-9+\-() #]", "", p)
            p = re.sub(r"\s+", " ", p).strip()
            return p if p else None

        out["phone"] = clean_phone(out["phone"])
        out["mobile"] = clean_phone(out["mobile"])
        out["company_phone"] = clean_phone(out["company_phone"])

        return out


def new_job_id() -> str:
    return uuid.uuid4().hex


