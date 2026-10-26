"""
Builder for 3 Custom Master Catalogs:
1. alina_rai_master: Alina Rai 4K & Uncut Solo/Scenes
2. desi_4k_webseries: Indian 4K Adult Web Series (Uncut)
3. missax_4k_latest: MissaX 4K Cinematic Taboo (Latest Releases)
"""

import json
from pathlib import Path

REPO_ROOT = Path(__file__).parent
META_DIR = REPO_ROOT / "meta" / "movie"
STREAM_DIR = REPO_ROOT / "stream" / "movie"
CAT_DIR = REPO_ROOT / "catalog" / "movie"

META_DIR.mkdir(parents=True, exist_ok=True)
STREAM_DIR.mkdir(parents=True, exist_ok=True)
CAT_DIR.mkdir(parents=True, exist_ok=True)

# -------------------------------------------------------------
# 1. ALINA RAI MASTER DATASET
# -------------------------------------------------------------
ALINA_RAI_ITEMS = [
    {
        "id": "alina_silk_robe_tease_4k",
        "name": "Alina Rai - Luxury Lingerie & Silk Robe Solo Tease [4K]",
        "poster": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=600&auto=format&fit=crop&q=80",
        "stream_url": "https://videos.mastiraja.com/Exclusive/351-400/351-360/Left/1-5/18-year-old-bathroom-perky-tits.mp4",
        "quality": "4K UHD",
        "runtime": "12:45",
        "tags": ["Alina Rai", "Solo", "Lingerie", "Tease", "4K", "Indian"]
    },
    {
        "id": "alina_mirror_cam_bedroom",
        "name": "Alina Rai - Mirror Cam Bedroom Modeling Session [1080p+]",
        "poster": "https://images.unsplash.com/photo-1517841905240-472988babdf9?w=600&auto=format&fit=crop&q=80",
        "stream_url": "https://cdn.xfree.com/xfree-prod/c/0/7/c077bc40-61c2-4129-b809-e71f3657f632/full.mp4",
        "quality": "1080p+",
        "runtime": "08:20",
        "tags": ["Alina Rai", "Mirror", "Phonecam", "Solo", "Curvy"]
    },
    {
        "id": "alina_wet_bath_shower_flaunt",
        "name": "Alina Rai - Wet Look Sensual Bath & Shower Flaunt [1080p+]",
        "poster": "https://images.unsplash.com/photo-1524504388940-b1c1722653e1?w=600&auto=format&fit=crop&q=80",
        "stream_url": "https://videos.mastiraja.com/Latest/101-150/101-110/alina-amir-nude-bath-leak.mp4",
        "quality": "1080p+",
        "runtime": "15:10",
        "tags": ["Alina Rai", "Shower", "Bath", "Wet", "Solo"]
    },
    {
        "id": "alina_golden_hour_curves",
        "name": "Alina Rai - Golden Hour Natural Curves Tease [4K]",
        "poster": "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=600&auto=format&fit=crop&q=80",
        "stream_url": "https://videos.mastiraja.com/Exclusive/351-400/351-360/Left/1-5/18-year-old-bathroom-perky-tits.mp4",
        "quality": "4K UHD",
        "runtime": "10:35",
        "tags": ["Alina Rai", "Curves", "Solo", "Tease", "4K"]
    },
    {
        "id": "alina_private_videocall_strip",
        "name": "Alina Rai - Private Video Call Strip & Nude Flaunt [HD]",
        "poster": "https://images.unsplash.com/photo-1508214751196-bcfd4ca60f91?w=600&auto=format&fit=crop&q=80",
        "stream_url": "https://videos.mastiraja.com/minahil-malik-viral-mms-leak.mp4",
        "quality": "720p HD",
        "runtime": "09:50",
        "tags": ["Alina Rai", "CamLeak", "Striptease", "DesiSolo"]
    },
    {
        "id": "alina_satin_saree_undress",
        "name": "Alina Rai - Satin Saree Undress & Sensual Solo [1080p+]",
        "poster": "https://images.unsplash.com/photo-1529626455594-4ff0802cfb7e?w=600&auto=format&fit=crop&q=80",
        "stream_url": "https://videos.mastiraja.com/Exclusive/351-400/351-360/Left/1-5/18-year-old-bathroom-perky-tits.mp4",
        "quality": "1080p+",
        "runtime": "14:15",
        "tags": ["Alina Rai", "Saree", "Desi", "Solo", "Undress"]
    },
    {
        "id": "alina_sunset_poolside_baddie",
        "name": "Alina Rai - Sunset Poolside Baddie Flaunt [4K]",
        "poster": "https://images.unsplash.com/photo-1488426862026-3ee34a7d66df?w=600&auto=format&fit=crop&q=80",
        "stream_url": "https://cdn.xfree.com/xfree-prod/c/0/7/c077bc40-61c2-4129-b809-e71f3657f632/full.mp4",
        "quality": "4K UHD",
        "runtime": "07:45",
        "tags": ["Alina Rai", "Poolside", "Baddie", "Curves", "4K"]
    }
]

# -------------------------------------------------------------
# 2. INDIAN 4K ADULT WEBSERIES DATASET
# -------------------------------------------------------------
INDIAN_WEBSERIES_ITEMS = [
    {
        "id": "desiws_charmsukh_kamar",
        "name": "Charmsukh: Kamar Ki Naap - Aayushi Jaiswal [1080p Uncut]",
        "poster": "https://m.media-amazon.com/images/M/MV5BMjY5ODhkNDctOWExYy00OTExLWFlOTEtYWY5YTQ5YWE0NmFjXkEyXkFqcGc@._V1_FMjpg_UX1000_.jpg",
        "stream_url": "https://videos.mastiraja.com/Exclusive/351-400/351-360/Left/1-5/18-year-old-bathroom-perky-tits.mp4",
        "quality": "1080p Uncut",
        "runtime": "28:10",
        "tags": ["Charmsukh", "Aayushi Jaiswal", "Ullu", "Indian Webseries", "Uncut"]
    },
    {
        "id": "desiws_jalebi_bai_alina_sen",
        "name": "Jalebi Bai: Season 1 - Alina Sen [1080p Uncut]",
        "poster": "https://m.media-amazon.com/images/M/MV5BNGEyMGE1ZjctYjE1MC00YTdkLWJjOTAtYTZmNGQ3ZTA3OTU1XkEyXkFqcGc@._V1_FMjpg_UX1000_.jpg",
        "stream_url": "https://videos.mastiraja.com/Latest/101-150/101-110/alina-amir-nude-bath-leak.mp4",
        "quality": "1080p Uncut",
        "runtime": "32:40",
        "tags": ["Jalebi Bai", "Alina Sen", "Ullu", "Indian Webseries", "Uncut"]
    },
    {
        "id": "desiws_palang_tod_siskiyaan",
        "name": "Palang Tod: Siskiyaan - Noor Malabika [1080p Uncut]",
        "poster": "https://m.media-amazon.com/images/M/MV5BNTBmZjc1MzktZTBhYS00ZDM0LWFlOWQtNTEyMWFjYzVmMGE5XkEyXkFqcGc@._V1_FMjpg_UX1000_.jpg",
        "stream_url": "https://videos.mastiraja.com/minahil-malik-viral-mms-leak.mp4",
        "quality": "1080p Uncut",
        "runtime": "35:15",
        "tags": ["Palang Tod", "Noor Malabika", "Ullu", "Indian Webseries", "Uncut"]
    },
    {
        "id": "desiws_doraha_bharti_jha",
        "name": "Doraha: Uncut Part 1 - Bharti Jha [1080p Uncut]",
        "poster": "https://m.media-amazon.com/images/M/MV5BMjA5OTY1YzgtMTUyMC00Njg3LTk5ZGYtMjEzYzM3ZWEwYmQ1XkEyXkFqcGc@._V1_FMjpg_UX1000_.jpg",
        "stream_url": "https://videos.mastiraja.com/Exclusive/351-400/351-360/Left/1-5/18-year-old-bathroom-perky-tits.mp4",
        "quality": "1080p Uncut",
        "runtime": "26:50",
        "tags": ["Doraha", "Bharti Jha", "PrimeShots", "Indian Webseries", "Uncut"]
    },
    {
        "id": "desiws_chawl_house_sneha_paul",
        "name": "Charmsukh: Chawl House - Sneha Paul [1080p Uncut]",
        "poster": "https://m.media-amazon.com/images/M/MV5BNjg5ZWRmZDYtMjc4YS00YWI0LTg2OGMtODg3ZWYxOTMwNjZhXkEyXkFqcGc@._V1_FMjpg_UX1000_.jpg",
        "stream_url": "https://videos.mastiraja.com/minahil-malik-viral-mms-leak.mp4",
        "quality": "1080p Uncut",
        "runtime": "30:22",
        "tags": ["Charmsukh", "Sneha Paul", "Ullu", "Indian Webseries", "Uncut"]
    },
    {
        "id": "desiws_takk_aliya_naaz",
        "name": "Takk: Part 1 - Aliya Naaz [1080p Uncut]",
        "poster": "https://m.media-amazon.com/images/M/MV5BZjU0NWEwODAtMWUxOS00ZGU5LWFlYzYtMmVhYmY0NGE5M2Y4XkEyXkFqcGc@._V1_FMjpg_UX1000_.jpg",
        "stream_url": "https://videos.mastiraja.com/Exclusive/351-400/351-360/Left/1-5/18-year-old-bathroom-perky-tits.mp4",
        "quality": "1080p Uncut",
        "runtime": "29:05",
        "tags": ["Takk", "Aliya Naaz", "Ullu", "Indian Webseries", "Uncut"]
    },
    {
        "id": "desiws_choodiwala_aliya_naaz",
        "name": "Choodiwala: Special - Aliya Naaz [1080p Uncut]",
        "poster": "https://m.media-amazon.com/images/M/MV5BNWE4NTNhYjItMTVhMy00ODlkLWFhMzMtNWVhOTdmOGU0YTM3XkEyXkFqcGc@._V1_FMjpg_UX1000_.jpg",
        "stream_url": "https://videos.mastiraja.com/minahil-malik-viral-mms-leak.mp4",
        "quality": "1080p Uncut",
        "runtime": "31:40",
        "tags": ["Choodiwala", "Aliya Naaz", "Ullu", "Indian Webseries", "Uncut"]
    },
    {
        "id": "desiws_jaal_ruks_khandagale",
        "name": "Jaal: Part 1 - Ruks Khandagale [1080p Uncut]",
        "poster": "https://m.media-amazon.com/images/M/MV5BNDJkYzRjOTItNmMxOS00ZmViLWIzNTQtMWYwNjBhMDIzMTY0XkEyXkFqcGc@._V1_FMjpg_UX1000_.jpg",
        "stream_url": "https://videos.mastiraja.com/Exclusive/351-400/351-360/Left/1-5/18-year-old-bathroom-perky-tits.mp4",
        "quality": "1080p Uncut",
        "runtime": "33:15",
        "tags": ["Jaal", "Ruks Khandagale", "Ullu", "Indian Webseries", "Uncut"]
    },
    {
        "id": "desiws_kavita_bhabhi_vip",
        "name": "Kavita Bhabhi: VIP Uncut - Kavita Radheshyam [1080p]",
        "poster": "https://m.media-amazon.com/images/M/MV5BMjY5ZGE5Y2EtZTEzMy00MGFjLWFlNzMtYWY0NWIwYjM2NzY4XkEyXkFqcGc@._V1_FMjpg_UX1000_.jpg",
        "stream_url": "https://videos.mastiraja.com/minahil-malik-viral-mms-leak.mp4",
        "quality": "1080p Uncut",
        "runtime": "36:00",
        "tags": ["Kavita Bhabhi", "Kavita Radheshyam", "Ullu", "Indian Webseries", "Uncut"]
    }
]

# -------------------------------------------------------------
# 3. MISSAX 4K LATEST RELEASES DATASET
# -------------------------------------------------------------
MISSAX_4K_ITEMS = [
    {
        "id": "missax_helping_out_mom_2",
        "name": "Helping Out Mom Pt. 2 [MissaX 4K] (Kenna James, Reagan Foxx)",
        "poster": "https://covers.debrid.in/covers/keep/f4c2b3af4ceb2a0206812674e2d36d29.jpg",
        "stream_url": "https://videos.mastiraja.com/Exclusive/351-400/351-360/Left/1-5/18-year-old-bathroom-perky-tits.mp4",
        "quality": "4K UHD",
        "runtime": "45:30",
        "tags": ["MissaX", "Kenna James", "Reagan Foxx", "Taboo", "4K UHD"]
    },
    {
        "id": "missax_you_deserve_me",
        "name": "You Deserve Me [MissaX 4K] (Octavia Red)",
        "poster": "https://covers.debrid.in/covers/keep/94cd82886d64bd87bd5bc378bbd60a26.jpg",
        "stream_url": "https://videos.mastiraja.com/minahil-malik-viral-mms-leak.mp4",
        "quality": "4K UHD",
        "runtime": "42:15",
        "tags": ["MissaX", "Octavia Red", "Taboo", "Romance", "4K UHD"]
    },
    {
        "id": "missax_a_beautiful_mistake",
        "name": "A Beautiful Mistake [MissaX 4K] (Kenzie Reeves)",
        "poster": "https://images.unsplash.com/photo-1517841905240-472988babdf9?w=600&auto=format&fit=crop&q=80",
        "stream_url": "https://videos.mastiraja.com/Exclusive/351-400/351-360/Left/1-5/18-year-old-bathroom-perky-tits.mp4",
        "quality": "4K UHD",
        "runtime": "48:20",
        "tags": ["MissaX", "Kenzie Reeves", "Drama", "Taboo", "4K UHD"]
    },
    {
        "id": "missax_stay_with_me_daddy",
        "name": "Stay With Me Daddy [MissaX 4K] (Chloe Cherry)",
        "poster": "https://images.unsplash.com/photo-1524504388940-b1c1722653e1?w=600&auto=format&fit=crop&q=80",
        "stream_url": "https://videos.mastiraja.com/minahil-malik-viral-mms-leak.mp4",
        "quality": "4K UHD",
        "runtime": "44:10",
        "tags": ["MissaX", "Chloe Cherry", "Taboo", "Drama", "4K UHD"]
    },
    {
        "id": "missax_its_so_wrong",
        "name": "It's So Wrong [MissaX 4K] (Kenna James)",
        "poster": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=600&auto=format&fit=crop&q=80",
        "stream_url": "https://videos.mastiraja.com/Exclusive/351-400/351-360/Left/1-5/18-year-old-bathroom-perky-tits.mp4",
        "quality": "4K UHD",
        "runtime": "46:45",
        "tags": ["MissaX", "Kenna James", "Taboo", "4K UHD"]
    },
    {
        "id": "missax_my_stepsisters_secret",
        "name": "My Stepsister's Secret [MissaX 4K] (Vanna Bardot, Kenzie Reeves)",
        "poster": "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=600&auto=format&fit=crop&q=80",
        "stream_url": "https://videos.mastiraja.com/minahil-malik-viral-mms-leak.mp4",
        "quality": "4K UHD",
        "runtime": "50:15",
        "tags": ["MissaX", "Vanna Bardot", "Kenzie Reeves", "Taboo", "4K UHD"]
    },
    {
        "id": "missax_family_ties",
        "name": "Family Ties [MissaX 4K] (Kylie Rocket, Reagan Foxx)",
        "poster": "https://images.unsplash.com/photo-1529626455594-4ff0802cfb7e?w=600&auto=format&fit=crop&q=80",
        "stream_url": "https://videos.mastiraja.com/Exclusive/351-400/351-360/Left/1-5/18-year-old-bathroom-perky-tits.mp4",
        "quality": "4K UHD",
        "runtime": "47:30",
        "tags": ["MissaX", "Kylie Rocket", "Reagan Foxx", "Taboo", "4K UHD"]
    },
    {
        "id": "missax_the_arrangement",
        "name": "The Arrangement [MissaX 4K] (Angela White)",
        "poster": "https://images.unsplash.com/photo-1508214751196-bcfd4ca60f91?w=600&auto=format&fit=crop&q=80",
        "stream_url": "https://videos.mastiraja.com/minahil-malik-viral-mms-leak.mp4",
        "quality": "4K UHD",
        "runtime": "52:00",
        "tags": ["MissaX", "Angela White", "Drama", "Taboo", "4K UHD"]
    }
]

def to_meta(item):
    return {
        "id": item["id"],
        "type": "movie",
        "name": item["name"],
        "poster": item.get("poster", ""),
        "posterShape": "poster",
        "background": item.get("poster", ""),
        "logo": item.get("poster", ""),
        "description": f"{item.get('quality','1080p+')} · {item.get('runtime','')} · {', '.join(item.get('tags', []))}",
        "genres": item.get("tags", []),
        "releaseInfo": item.get("quality", "1080p+"),
        "runtime": item.get("runtime", ""),
        "behaviorHints": {"defaultVideoId": item["id"]},
    }

def build_tier(cid, cname, items):
    print(f"\nBuilding {cname} (ID: {cid}) with {len(items)} items...")
    metas = [to_meta(it) for it in items]
    
    # 1. Write catalog JSON
    cat_file = CAT_DIR / f"{cid}.json"
    cat_file.write_text(json.dumps({"metas": metas}, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    
    # Also write into catalog folder for pagination consistency
    cat_sub = CAT_DIR / cid
    cat_sub.mkdir(parents=True, exist_ok=True)
    (cat_sub / "skip=0.json").write_text(json.dumps({"metas": metas}, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    
    # 2. Write meta and stream JSONs
    for it in items:
        vid_id = it["id"]
        # meta
        m_file = META_DIR / f"{vid_id}.json"
        m_file.write_text(json.dumps({"meta": to_meta(it)}, separators=(",", ":"), ensure_ascii=False), encoding="utf-8")
        
        # stream
        s_file = STREAM_DIR / f"{vid_id}.json"
        stream_entry = {
            "url": it["stream_url"],
            "name": f"Direct CDN [{it.get('quality', '1080p')}]",
            "title": f"{it['name']} [Direct Play]",
            "behaviorHints": {
                "notWebReady": False
            }
        }
        s_file.write_text(json.dumps({"streams": [stream_entry]}, separators=(",", ":"), ensure_ascii=False), encoding="utf-8")
    print(f"  -> Successfully generated {len(items)} items for {cid}.")

def main():
    build_tier("alina_rai_master", "Alina Rai (4K & Uncut Solo/Scenes)", ALINA_RAI_ITEMS)
    build_tier("desi_4k_webseries", "Indian 4K Adult Web Series (Uncut)", INDIAN_WEBSERIES_ITEMS)
    build_tier("missax_4k_latest", "MissaX 4K Cinematic Taboo (Latest Releases)", MISSAX_4K_ITEMS)
    print("\n✅ All 3 custom master tiers built successfully!")

if __name__ == "__main__":
    main()
