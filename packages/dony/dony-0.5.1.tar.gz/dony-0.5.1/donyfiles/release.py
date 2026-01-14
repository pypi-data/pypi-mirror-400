from marklidenberg_donyfiles import release
import dony
import os
import asyncio

if __name__ == "__main__":
    os.chdir(dony.find_repo_root(__file__))
    asyncio.run(release())
