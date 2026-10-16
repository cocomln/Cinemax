import asyncio
from app.db.init_db import init_db
from app.ingestion.pipeline import pipeline

async def main():
    print("Initializing database...")
    init_db()
    print("Running initial ingestion pipeline with real data providers (AniList, TVmaze, Wikidata)...")
    result = await pipeline.run_pipeline()
    print("Initial ingestion complete!")
    print(result)

if __name__ == "__main__":
    asyncio.run(main())
