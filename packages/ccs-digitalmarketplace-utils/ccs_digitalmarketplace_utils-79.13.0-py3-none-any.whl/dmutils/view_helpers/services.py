def get_drafts(client, supplier_id, framework_slug):
    complete_drafts, unsubmitted_drafts = [], []

    for draft in client.find_draft_services_iter(supplier_id, framework=framework_slug):
        if draft['status'] in ('submitted', 'failed'):
            complete_drafts.append(draft)
        if draft['status'] == 'not-submitted':
            unsubmitted_drafts.append(draft)

    return unsubmitted_drafts, complete_drafts
