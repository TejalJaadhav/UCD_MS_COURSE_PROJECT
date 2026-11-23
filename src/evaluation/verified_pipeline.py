"""Run component decomposition followed by evidence selection and verification."""

from src.evaluation.rescore_sentence_evidence import judge_component
from src.evaluation.run_prompted import ask, predict


def predict_verified(model, claim, source):
    """Reuse original split checks and verify each component's selected evidence."""
    prediction, details = predict("components", model, claim, source)
    components = details.get("components")
    details["verification_version"] = 1
    if not components:
        return prediction, details

    labels = []
    for component in components:
        component["previous_label"] = component["label"]
        try:
            selection = judge_component(model, component)
            component["sentence_evidence_check"] = selection
            if selection["status"] != "valid":
                raise ValueError("Invalid evidence selection.")
            label = selection["response"]["label"]
            if label != "unsupported":
                result, usage = ask(
                    model,
                    "Verify whether the supplied evidence establishes the statement. "
                    "Use only this evidence. Do not supply missing facts from memory. "
                    "Preserve numbers, populations, dates, qualifiers and relationships. "
                    "A missing numerical value does not establish a claimed number. "
                    "Return supported only if every detail is established, contradicted "
                    "only for direct conflict, otherwise unsupported.",
                    {"statement": component["component"],
                     "evidence": selection["selected_evidence"]},
                    {"label": {"type": "string",
                               "enum": ["supported", "unsupported", "contradicted"]},
                     "reason": {"type": "string"}},
                )
                component["evidence_verification"] = {"response": result, "usage": usage}
                label = result["label"]
            component["label"] = label
        except ValueError as error:
            component["label"] = None
            component["verification_error"] = str(error)
        labels.append(component["label"])

    details["previous_prediction"] = prediction
    if None in labels:
        return None, details
    if all(label == "supported" for label in labels):
        return "complete_support", details
    if "supported" in labels:
        return "partial_support", details
    return "no_support", details
