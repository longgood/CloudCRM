# -*- encoding: utf-8 -*-

import os
from typing import Any, Dict

from flask import current_app, jsonify, render_template, request, send_file
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from apps import db
from apps.authentication.models import TCustomer, TFacility
from apps.namecard import blueprint
from apps.namecard.service import NameCardProcessor, OpenAIBusinessCardExtractor, new_job_id


def _uploads_root() -> str:
    root = current_app.config.get("UPLOAD_FOLDER", "D:/testdata")
    return os.path.abspath(root)


def _job_dir(job_id: str) -> str:
    return os.path.join(_uploads_root(), "namecard_ocr", job_id)


def _safe_join_under_root(root: str, *parts: str) -> str:
    root_abs = os.path.abspath(root)
    path = os.path.abspath(os.path.join(root_abs, *parts))
    if not path.startswith(root_abs + os.sep) and path != root_abs:
        raise ValueError("Invalid path")
    return path


@blueprint.route("/namecard_ocr", methods=["GET"])
@login_required
def namecard_ocr_page():
    return render_template("namecard/index.html", segment="namecard_ocr")


@blueprint.route("/namecard_ocr/analyze", methods=["POST"])
@login_required
def namecard_ocr_analyze():
    if "file" not in request.files:
        return jsonify({"ok": False, "error": "missing file"}), 400

    f = request.files["file"]
    if not f or not f.filename:
        return jsonify({"ok": False, "error": "empty filename"}), 400

    job_id = new_job_id()
    job_dir = _job_dir(job_id)
    os.makedirs(job_dir, exist_ok=True)

    filename = secure_filename(f.filename)
    original_path = os.path.join(job_dir, f"original_{filename}")
    f.save(original_path)

    # 1) Segment into crops
    processor = NameCardProcessor(job_dir)
    cards = processor.segment_and_save(original_path)

    # 2) OCR each crop with OpenAI Vision
    extractor = OpenAIBusinessCardExtractor()
    results = []
    for c in cards:
        crop_path = os.path.join(job_dir, "crops", c.filename)
        fields = extractor.extract_fields(crop_path)
        results.append(
            {
                "filename": c.filename,
                "image_url": f"/namecard_ocr/image/{job_id}/{c.filename}",
                "bbox": {"x": c.bbox[0], "y": c.bbox[1], "w": c.bbox[2], "h": c.bbox[3]},
                "fields": fields,
            }
        )

    return jsonify({"ok": True, "job_id": job_id, "cards": results})


@blueprint.route("/namecard_ocr/image/<job_id>/<filename>", methods=["GET"])
@login_required
def namecard_ocr_image(job_id: str, filename: str):
    root = _uploads_root()
    safe_job = secure_filename(job_id)
    safe_name = secure_filename(filename)
    path = _safe_join_under_root(root, "namecard_ocr", safe_job, "crops", safe_name)
    if not os.path.exists(path):
        return "Image not found", 404
    return send_file(path, mimetype="image/jpeg")


@blueprint.route("/namecard_ocr/confirm", methods=["POST"])
@login_required
def namecard_ocr_confirm():
    data: Dict[str, Any] = request.get_json(silent=True) or {}
    job_id = secure_filename(str(data.get("job_id") or ""))
    filename = secure_filename(str(data.get("filename") or ""))
    fields = data.get("fields") or {}

    if not job_id or not filename:
        return jsonify({"ok": False, "error": "missing job_id/filename"}), 400

    # Map OCR fields -> DB fields (existing schema)
    person_name = (fields.get("name") or "").strip()
    job_title = (fields.get("job_title") or "").strip()
    email = (fields.get("email") or "").strip()
    phone = (fields.get("phone") or "").strip()
    mobile = (fields.get("mobile") or "").strip()
    company_name = (fields.get("company_name") or "").strip()
    company_phone = (fields.get("company_phone") or "").strip()
    address = (fields.get("address") or "").strip()

    if not person_name:
        return jsonify({"ok": False, "error": "name is required"}), 400

    facility_id = None
    if company_name:
        facility = TFacility.query.filter_by(displayName=company_name).first()
        if not facility:
            facility = TFacility({})
            facility.displayName = company_name
            if address:
                facility.address = address
            if company_phone:
                facility.phone = company_phone
            facility.add_new()
        facility_id = facility.uid

    customer = TCustomer.query.filter_by(realName=person_name, jobTitle=job_title).first()
    if not customer:
        customer = TCustomer()
        customer.managerID = current_user.uid
        customer.realName = person_name
        customer.jobTitle = job_title
        if facility_id:
            customer.facilityID = facility_id
        # Prefer mobile for cellPhone
        if mobile:
            customer.cellPhone = mobile
        elif phone:
            customer.cellPhone = phone
        if phone:
            customer.localPhone = phone
        if email:
            customer.eMail = email

        db.session.add(customer)
        db.session.commit()
        created = True
    else:
        created = False

    return jsonify({"ok": True, "created": created, "customer_uid": customer.uid})


