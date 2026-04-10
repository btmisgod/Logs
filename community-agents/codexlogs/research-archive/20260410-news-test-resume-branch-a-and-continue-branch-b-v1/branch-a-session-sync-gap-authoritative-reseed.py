import asyncio, json
from sqlalchemy import select
from app.db.session import SessionLocal
from app.models.group import Group
from app.services.group_session import ensure_group_session_fact

GROUP_SLUG = "news-test"

async def main():
    async with SessionLocal() as session:
        group = await session.scalar(select(Group).where(Group.slug == GROUP_SLUG))
        if group is None:
            raise SystemExit("group_not_found")
        metadata = dict(group.metadata_json or {})
        community = dict(metadata.get("community_v2") or {})
        before = dict(community.get("group_session") or {})
        community["group_session"] = {}
        metadata["community_v2"] = community
        group.metadata_json = metadata
        seeded = ensure_group_session_fact(group)
        await session.commit()
        await session.refresh(group)
        after = dict((group.metadata_json or {}).get("community_v2", {}).get("group_session") or {})
        print(json.dumps({
            "group_id": str(group.id),
            "group_slug": group.slug,
            "before": before,
            "seeded": seeded,
            "after": after,
        }, ensure_ascii=False))

asyncio.run(main())
