def detect_study_type(input_text: str) -> str:
    text = (input_text or "").lower()

    modality_keywords = {
        "CT": ["ct", "computed tomography"],
        "MRI": ["mri", "mr ", "magnetic resonance"],
        "Ultrasound": ["ultrasound", "sonography", "doppler", "usg"],
        "X-ray": ["x-ray", "xray", "radiograph"],
    }
    body_part_keywords = {
        "Brain": ["brain", "intracranial", "gangliocapsular", "ventricle", "midline shift", "hemorrhage", "skull"],
        "Spine": ["spine", "vertebral", "intervertebral", "disc", "facet", "spinal canal", "nerve root", "alignment"],
        "Chest": ["chest", "lung", "pleural", "mediastinum", "pulmonary"],
        "Abdomen": ["abdomen", "liver", "gallbladder", "pancreas", "spleen", "kidney", "renal"],
        "Pelvis": ["pelvis", "uterus", "ovary", "prostate", "bladder"],
        "Neck": ["neck", "thyroid", "cervical"],
    }

    detected_modality = next(
        (label for label, keywords in modality_keywords.items() if any(keyword in text for keyword in keywords)),
        None,
    )
    detected_body_part = next(
        (label for label, keywords in body_part_keywords.items() if any(keyword in text for keyword in keywords)),
        None,
    )

    if detected_modality and detected_body_part:
        return f"{detected_modality} {detected_body_part}"
    if detected_body_part == "Brain":
        return "CT Brain"
    if detected_body_part == "Spine":
        return "MRI Spine"
    if detected_body_part:
        return f"Radiology {detected_body_part}"
    return "General Radiology"
