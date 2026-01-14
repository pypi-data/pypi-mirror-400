def supplier_made_application(
    supplier_on_framework,
    complete_drafts,
    declaration_status,
    application_company_details_confirmed,
    lot_questions_responses_status,
    technical_ability_certificate_status,
    lot_pricings_status,
    fvra_status,
):
    return supplier_on_framework or (
        len(complete_drafts) > 0
        and declaration_status == 'complete'
        and application_company_details_confirmed
        and lot_questions_responses_status in ['not_required', 'complete']
        and technical_ability_certificate_status in [
            'not_required',
            'complete',
            'pending',
        ]
        and lot_pricings_status in ['not_required', 'complete']
        and fvra_status in ['not_required', 'complete']
    )
