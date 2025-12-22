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

    def crop_by_rectangles(self, input_image_path: str, rectangles: List[Dict[str, int]]) -> List[SegmentedCard]:
        """
        Crop image based on user-provided rectangles (from interactive selection).
        
        Args:
            input_image_path: path to the original image
            rectangles: list of dicts with {x, y, w, h} in image coordinates
            
        Returns:
            List of SegmentedCard with cropped images saved to crops_dir
        """
        img = cv2.imread(input_image_path)
        if img is None:
            raise ValueError(f"Failed to read image: {input_image_path}")

        h, w = img.shape[:2]
        if self.debug:
            print(f"[NameCardProcessor] crop_by_rectangles: input={input_image_path} size={w}x{h}")
            print(f"[NameCardProcessor] rectangles={rectangles}")

        cards: List[SegmentedCard] = []
        for idx, rect in enumerate(rectangles, start=1):
            x = max(0, int(rect.get("x", 0)))
            y = max(0, int(rect.get("y", 0)))
            rw = int(rect.get("w", 0))
            rh = int(rect.get("h", 0))
            
            # Clamp to image bounds
            x2 = min(w, x + rw)
            y2 = min(h, y + rh)
            
            if x2 <= x or y2 <= y:
                if self.debug:
                    print(f"[NameCardProcessor] Skipping invalid rect {idx}: {rect}")
                continue
            
            # Crop the region
            crop = img[y:y2, x:x2].copy()
            
            if crop.size == 0:
                if self.debug:
                    print(f"[NameCardProcessor] Skipping empty crop {idx}")
                continue
            
            ch, cw = crop.shape[:2]
            
            # Add small padding (helps OCR)
            pad = int(max(4, min(20, 0.02 * max(cw, ch))))
            crop = cv2.copyMakeBorder(crop, pad, pad, pad, pad, cv2.BORDER_REPLICATE)
            
            # Rotate to landscape if needed
            crop_h, crop_w = crop.shape[:2]
            if crop_h > crop_w * 1.1:
                crop = cv2.rotate(crop, cv2.ROTATE_90_CLOCKWISE)
            
            filename = f"card_{idx:03d}.jpg"
            out_path = os.path.join(self.crops_dir, filename)
            cv2.imwrite(out_path, crop)
            
            final_h, final_w = crop.shape[:2]
            cards.append(SegmentedCard(
                filename=filename,
                width=final_w,
                height=final_h,
                bbox=(x, y, x2 - x, y2 - y)
            ))
            
            if self.debug:
                print(f"[NameCardProcessor] Saved crop {idx}: {filename} ({final_w}x{final_h})")

        if not cards:
            # Fallback: save whole image if no valid crops
            filename = "card_001.jpg"
            out_path = os.path.join(self.crops_dir, filename)
            cv2.imwrite(out_path, img)
            return [SegmentedCard(filename=filename, width=w, height=h, bbox=(0, 0, w, h))]

        return cards

    def _detect_candidate_boxes(self, img) -> List[Any]:
        """
        Returns list of 4-point quads (float32) in original image coordinates.
        Implements multiple detection pipelines and picks the best result.
        """
        h, w = img.shape[:2]
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray_blur = cv2.GaussianBlur(gray, (5, 5), 0)

        # Heuristics for business cards
        img_area = float(w * h)
        # For a 10-card grid on A4 scan, each card is ~1/12 of the page
        min_card_area = max(0.02 * img_area, 30_000)  # ~2% of image
        max_card_area = 0.25 * img_area  # no single card > 25% of page
        
        # For contour filtering (before minAreaRect)
        min_contour_area = max(0.005 * img_area, 5_000)

        debug_info = {
            "image": {"w": w, "h": h},
            "min_card_area": min_card_area,
            "max_card_area": max_card_area,
            "candidates": [],
            "pipeline_counts": {},
            "chosen_pipeline": None,
        }

        def accept_rect(rect, source: str, min_ar: float = 1.2, max_ar: float = 4.0):
            """Check if a minAreaRect is card-shaped and return its box points."""
            (cx, cy), (rw, rh), angle = rect
            if rw <= 0 or rh <= 0:
                return None
            ar = max(rw, rh) / (min(rw, rh) + 1e-6)
            if ar < min_ar or ar > max_ar:
                return None
            area_est = float(rw * rh)
            if area_est < min_card_area or area_est > max_card_area:
                return None
            box = cv2.boxPoints(rect)
            debug_info["candidates"].append({
                "source": source,
                "center": [float(cx), float(cy)],
                "size": [float(rw), float(rh)],
                "angle": float(angle),
                "aspect_ratio": float(ar),
                "area_est": float(area_est),
                "bbox": list(self._quad_bbox(box)),
            })
            return box

        def dedupe_quads(quads_in: List[Any], threshold: int = 30) -> List[Any]:
            """Remove near-duplicate quads based on center distance."""
            if not quads_in:
                return []
            quads_in = list(quads_in)
            # Sort by y then x
            quads_in.sort(key=lambda q: (self._quad_bbox(q)[1], self._quad_bbox(q)[0]))
            deduped: List[Any] = []
            for q in quads_in:
                x, y, bw, bh = self._quad_bbox(q)
                cx, cy = x + bw / 2, y + bh / 2
                too_close = False
                for oq in deduped:
                    ox, oy, obw, obh = self._quad_bbox(oq)
                    ocx, ocy = ox + obw / 2, oy + obh / 2
                    dist = ((cx - ocx) ** 2 + (cy - ocy) ** 2) ** 0.5
                    if dist < threshold:
                        too_close = True
                        break
                if not too_close:
                    deduped.append(q)
            return deduped

        quads_edges: List[Any] = []
        quads_thresh: List[Any] = []
        quads_scan: List[Any] = []

        # ========== Pipeline A: Canny edge detection ==========
        edges = cv2.Canny(gray_blur, 30, 100)
        kernel_edge = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        edges = cv2.dilate(edges, kernel_edge, iterations=2)
        edges = cv2.erode(edges, kernel_edge, iterations=1)
        if self.debug:
            self._write_debug_image("01_edges.jpg", edges)

        contours_edge, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if self.debug:
            print(f"[NameCardProcessor] Pipeline A (edges): {len(contours_edge)} contours")

        for cnt in contours_edge:
            if cv2.contourArea(cnt) < min_contour_area:
                continue
            rect = cv2.minAreaRect(cnt)
            box = accept_rect(rect, "edges")
            if box is not None:
                quads_edges.append(box)

        # ========== Pipeline B: Adaptive threshold ==========
        thr = cv2.adaptiveThreshold(gray_blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                     cv2.THRESH_BINARY_INV, 31, 5)
        k_close_b = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 15))
        morph_b = cv2.morphologyEx(thr, cv2.MORPH_CLOSE, k_close_b, iterations=2)
        morph_b = cv2.morphologyEx(morph_b, cv2.MORPH_OPEN, 
                                    cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5)), iterations=1)
        if self.debug:
            self._write_debug_image("02_thresh.jpg", thr)
            self._write_debug_image("03_morph.jpg", morph_b)

        contours_thresh, _ = cv2.findContours(morph_b, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if self.debug:
            print(f"[NameCardProcessor] Pipeline B (thresh): {len(contours_thresh)} contours")

        for cnt in contours_thresh:
            if cv2.contourArea(cnt) < min_contour_area:
                continue
            rect = cv2.minAreaRect(cnt)
            box = accept_rect(rect, "thresh")
            if box is not None:
                quads_thresh.append(box)

        # ========== Pipeline C: Scan/Grid detection (for white background scans) ==========
        # This is the KEY pipeline for your 10-card scanned image.
        # Strategy:
        # 1. Detect all non-white pixels (text, logos, borders)
        # 2. Use VERY large morphology to merge all content within each card
        # 3. Find connected components (each should be one card)

        # Step 1: Create mask of non-white pixels (with some tolerance for near-white)
        # Use multiple thresholds and combine for robustness
        mask_tight = (gray < 240).astype(np.uint8) * 255  # very non-white
        mask_loose = (gray < 250).astype(np.uint8) * 255  # slightly non-white
        
        # Use Otsu's threshold as well for automatic level detection
        _, otsu_mask = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        
        # Combine masks
        combined_mask = cv2.bitwise_or(mask_tight, otsu_mask)
        
        if self.debug:
            self._write_debug_image("05_scan_mask_tight.jpg", mask_tight)
            self._write_debug_image("05_scan_mask_otsu.jpg", otsu_mask)
            self._write_debug_image("05_scan_mask_combined.jpg", combined_mask)

        # Step 2: HUGE morphology close to merge all text/logos within a card
        # For a typical A4 scan at 150-300 DPI, cards are ~400-800px wide
        # We need a kernel that can bridge gaps of 50-150px between text lines
        
        # Adaptive kernel size based on image dimensions
        # For 1200px height, kernel ~ 60-80px; for 2400px, kernel ~ 120-160px
        base_kernel_size = int(min(w, h) / 15)  # ~6-7% of smaller dimension
        base_kernel_size = max(40, min(150, base_kernel_size))  # clamp to [40, 150]
        if base_kernel_size % 2 == 0:
            base_kernel_size += 1  # must be odd
        
        if self.debug:
            print(f"[NameCardProcessor] Pipeline C: base_kernel_size={base_kernel_size}")

        # Apply morphology in stages for better merging
        k_dilate1 = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 15))
        k_close1 = cv2.getStructuringElement(cv2.MORPH_RECT, (base_kernel_size, base_kernel_size))
        k_close2 = cv2.getStructuringElement(cv2.MORPH_RECT, (base_kernel_size // 2, base_kernel_size // 2))
        
        # First dilate to connect nearby text
        scan_morph = cv2.dilate(combined_mask, k_dilate1, iterations=2)
        # Then close to merge everything within a card
        scan_morph = cv2.morphologyEx(scan_morph, cv2.MORPH_CLOSE, k_close1, iterations=2)
        # Additional close pass
        scan_morph = cv2.morphologyEx(scan_morph, cv2.MORPH_CLOSE, k_close2, iterations=2)
        # Clean up small noise
        scan_morph = cv2.morphologyEx(scan_morph, cv2.MORPH_OPEN, 
                                       cv2.getStructuringElement(cv2.MORPH_RECT, (10, 10)), iterations=1)
        
        if self.debug:
            self._write_debug_image("06_scan_morph.jpg", scan_morph)

        # Step 3: Find contours (each should be one card now)
        contours_scan, _ = cv2.findContours(scan_morph, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if self.debug:
            print(f"[NameCardProcessor] Pipeline C (scan): {len(contours_scan)} contours after morph")

        for cnt in contours_scan:
            rect = cv2.minAreaRect(cnt)
            # More lenient aspect ratio for scan pipeline (cards may be slightly skewed)
            box = accept_rect(rect, "scan", min_ar=1.1, max_ar=5.0)
            if box is not None:
                quads_scan.append(box)

        # ========== Pipeline D: Alternative - edge-based rectangle detection ==========
        # Sometimes morphology doesn't work well; try finding rectangles via contour approximation
        quads_contour: List[Any] = []
        
        # Use bilateral filter to smooth while preserving edges
        bilateral = cv2.bilateralFilter(gray, 9, 75, 75)
        edges_bilateral = cv2.Canny(bilateral, 20, 80)
        edges_bilateral = cv2.dilate(edges_bilateral, cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3)), iterations=2)
        
        if self.debug:
            self._write_debug_image("07_bilateral_edges.jpg", edges_bilateral)
        
        contours_bilateral, _ = cv2.findContours(edges_bilateral, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for cnt in contours_bilateral:
            area = cv2.contourArea(cnt)
            if area < min_contour_area:
                continue
            # Approximate contour to polygon
            peri = cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, 0.02 * peri, True)
            # If it's roughly rectangular (4-6 vertices)
            if 4 <= len(approx) <= 8:
                rect = cv2.minAreaRect(cnt)
                box = accept_rect(rect, "contour", min_ar=1.1, max_ar=5.0)
                if box is not None:
                    quads_contour.append(box)
        
        if self.debug:
            print(f"[NameCardProcessor] Pipeline D (contour): {len(quads_contour)} candidates")

        # ========== Dedup and choose best pipeline ==========
        quads_edges_d = dedupe_quads(quads_edges, threshold=50)
        quads_thresh_d = dedupe_quads(quads_thresh, threshold=50)
        quads_scan_d = dedupe_quads(quads_scan, threshold=50)
        quads_contour_d = dedupe_quads(quads_contour, threshold=50)

        debug_info["pipeline_counts"] = {
            "edges": len(quads_edges_d),
            "thresh": len(quads_thresh_d),
            "scan": len(quads_scan_d),
            "contour": len(quads_contour_d),
        }

        if self.debug:
            print(f"[NameCardProcessor] Pipeline counts: edges={len(quads_edges_d)}, thresh={len(quads_thresh_d)}, scan={len(quads_scan_d)}, contour={len(quads_contour_d)}")

        # Choose best pipeline based on number of detections
        # For multi-card scans, prefer the pipeline that finds the most cards (within reason)
        pipeline_results = [
            ("scan", quads_scan_d),
            ("contour", quads_contour_d),
            ("thresh", quads_thresh_d),
            ("edges", quads_edges_d),
        ]
        
        # Sort by count (descending), prefer pipelines finding 3-20 cards
        def score_pipeline(name_quads):
            name, quads = name_quads
            count = len(quads)
            if 3 <= count <= 20:
                return (1000 + count, count)  # prefer reasonable counts
            elif count > 0:
                return (count, count)
            return (0, 0)
        
        pipeline_results.sort(key=score_pipeline, reverse=True)
        best_name, best_quads = pipeline_results[0]
        
        # If best has reasonable count, use it; otherwise combine all
        if len(best_quads) >= 3:
            chosen = best_quads
            debug_info["chosen_pipeline"] = best_name
        else:
            # Combine all and dedupe
            all_quads = quads_edges_d + quads_thresh_d + quads_scan_d + quads_contour_d
            chosen = dedupe_quads(all_quads, threshold=50)
            debug_info["chosen_pipeline"] = "combined"

        if self.debug:
            debug_info["final_count"] = len(chosen)
            with open(os.path.join(self.debug_dir, "boxes.json"), "w", encoding="utf-8") as f:
                json.dump(debug_info, f, ensure_ascii=False, indent=2)
            
            # Draw final overlay
            overlay = img.copy()
            for idx, q in enumerate(chosen, 1):
                pts = q.reshape((-1, 1, 2)).astype(np.int32)
                cv2.polylines(overlay, [pts], True, (0, 255, 0), 4)
                x, y, _, _ = self._quad_bbox(q)
                cv2.putText(overlay, str(idx), (int(x) + 10, int(y) + 40),
                           cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 3)
            self._write_debug_image("04_boxes_overlay.jpg", overlay)
            print(f"[NameCardProcessor] Chosen: {debug_info['chosen_pipeline']} with {len(chosen)} boxes")

        return chosen

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

        # Add small padding to avoid border clipping (helps OCR too).
        pad = int(max(6, min(40, 0.02 * max(maxW, maxH))))
        warped = cv2.copyMakeBorder(warped, pad, pad, pad, pad, cv2.BORDER_REPLICATE)

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
        self.api_key = api_key or os.getenv("OPENAI_API_KEY_CRM")
        self.model = model or os.getenv("OPENAI_VISION_MODEL", "gpt-4o-mini")

        if not self.api_key:
            raise ValueError("OPENAI_API_KEY_CRM is not set")

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
            text={
                "format": {
                    "type": "json_schema",
                    # openai==1.75.0 Responses API requires `text.format.name`
                    "name": "business_card",
                    "schema": schema,
                    "strict": True,
                }
            },
        )

        # Responses API: `output_text` is convenient, but even with json_schema the model may
        # occasionally wrap JSON with extra text. We'll parse robustly.
        def _coerce_mapping(obj):
            # Support both SDK objects (attrs) and dicts.
            if obj is None:
                return None
            if isinstance(obj, dict):
                return obj
            return None

        def _iter_output_text_parts(response_obj):
            out = getattr(response_obj, "output", None)
            if not out:
                return
            for item in out:
                content = getattr(item, "content", None)
                if content is None:
                    as_dict = _coerce_mapping(item)
                    content = as_dict.get("content") if as_dict else None
                if not content:
                    continue
                for part in content:
                    ptype = getattr(part, "type", None)
                    if ptype is None:
                        as_dict = _coerce_mapping(part)
                        ptype = as_dict.get("type") if as_dict else None
                    if ptype not in ("output_text", "text"):
                        continue
                    ptext = getattr(part, "text", None)
                    if ptext is None:
                        as_dict = _coerce_mapping(part)
                        ptext = as_dict.get("text") if as_dict else None
                    if ptext:
                        yield str(ptext)

        text = (getattr(resp, "output_text", None) or "").strip()
        if not text:
            parts = list(_iter_output_text_parts(resp))
            text = "\n".join(parts).strip()
        if not text:
            # best-effort fallback: stringify whole response for debugging/visibility
            text = str(resp)

        def _best_effort_json_loads(s: str):
            # 1) Direct JSON
            try:
                return json.loads(s)
            except Exception:
                pass
            # 2) Find first JSON object/array within the string
            dec = json.JSONDecoder()
            for i, ch in enumerate(s):
                if ch not in "{[":
                    continue
                try:
                    obj, _end = dec.raw_decode(s[i:])
                    return obj
                except Exception:
                    continue
            raise ValueError("No JSON object found in response text")

        try:
            data = _best_effort_json_loads(text)
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


