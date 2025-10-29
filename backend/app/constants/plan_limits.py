PLAN_LIMITS = {
    "free": {
        "images_per_month": 3
    },
    "monthly": {
        "images_per_month": 100
    },
    "yearly": {
        "images_per_month": 100
    }
}

def get_plan_limit(plan_name: str) -> int:
    """Get the image generation limit for a given plan"""
    plan_key = plan_name.lower()
    
    if "yearly" in plan_key or "annual" in plan_key:
        return PLAN_LIMITS["yearly"]["images_per_month"]
    elif "monthly" in plan_key or "month" in plan_key:
        return PLAN_LIMITS["monthly"]["images_per_month"]
    else:
        return PLAN_LIMITS["free"]["images_per_month"]
