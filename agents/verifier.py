def verify_results(results):

    verified = True

    for r in results:
        if not r.get("output"):
            verified = False

    return {
        "verified": verified,
        "results": results
    }
