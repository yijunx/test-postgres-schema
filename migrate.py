from app.utils.db import get_ready_for_tenant, migrate_all_schemas


if __name__ == "__main__":
    # migrate_all_schemas()
    get_ready_for_tenant("tenant003")