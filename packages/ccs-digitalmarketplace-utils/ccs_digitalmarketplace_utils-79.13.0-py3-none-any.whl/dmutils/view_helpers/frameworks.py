from functools import wraps
from flask import abort

from dmapiclient import APIError


def get_framework_or_404(client, framework_slug, allowed_statuses=None):
    if allowed_statuses is None:
        allowed_statuses = ['open', 'pending', 'standstill', 'live']

    framework = client.get_framework(framework_slug)['frameworks']

    if allowed_statuses and framework['status'] not in allowed_statuses:
        abort(404)

    return framework


def get_supplier_framework_info(
    client,
    supplier_id,
    framework_slug,
    with_technical_ability_certificates=None,
    with_lot_questions_responses=None,
    with_lot_pricings=None,
    with_cdp_supplier_information=None,
    with_evaluation_scores=None,
):
    try:
        return client.get_supplier_framework_info(
            supplier_id,
            framework_slug,
            with_technical_ability_certificates=with_technical_ability_certificates,
            with_lot_questions_responses=with_lot_questions_responses,
            with_lot_pricings=with_lot_pricings,
            with_cdp_supplier_information=with_cdp_supplier_information,
            with_evaluation_scores=with_evaluation_scores,
        )['frameworkInterest']
    except APIError as e:
        if e.status_code == 404:
            return None

        abort(e.status_code)


def get_declaration_status_from_info(supplier_framework_info):
    if not supplier_framework_info or not supplier_framework_info.get('declaration'):
        return 'unstarted'

    return supplier_framework_info['declaration'].get('status', 'unstarted')


def _get_status_from_info(supplier_framework_info, field):
    if not supplier_framework_info or not supplier_framework_info.get(field):
        return 'not_required'

    return supplier_framework_info.get(field, 'not_required')


@wraps(_get_status_from_info)
def get_technical_ability_certificate_status_from_info(supplier_framework_info):
    return _get_status_from_info(supplier_framework_info, 'technicalAbilityCertificatesStatus')


@wraps(_get_status_from_info)
def get_lot_pricings_status_from_info(supplier_framework_info):
    return _get_status_from_info(supplier_framework_info, 'lotPricingsStatus')


@wraps(_get_status_from_info)
def get_lot_questions_responses_status_from_info(supplier_framework_info):
    return _get_status_from_info(supplier_framework_info, 'lotQuestionsResponsesStatus')


@wraps(_get_status_from_info)
def get_fvra_status_from_info(supplier_framework_info):
    return _get_status_from_info(supplier_framework_info, 'fvraStatus')
