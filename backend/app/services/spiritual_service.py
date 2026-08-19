import os
import json
import logging
import requests
import html
from datetime import datetime, timezone
from typing import Optional, Dict, Any, Tuple

_CHARACTER_CACHE: Dict[str, dict] = {}
from app.services.scripture_data import (
    GITA_CHAPTER_NAMES,
    GITA_CHAPTER_VERSE_COUNTS,
    RAMAYANA_DATASET,
    MAHABHARATA_DATASET
)

logger = logging.getLogger(__name__)

# Base date to anchor day 1 of the daily sequential reading (Today = Day 1)
EPOCH_START_DATE = datetime(2026, 8, 18).date()

TOTAL_GITA_VERSES = 700

def get_day_offset(target_date: Optional[datetime.date] = None) -> int:
    """Returns days elapsed since EPOCH_START_DATE (0-indexed)."""
    if not target_date:
        target_date = datetime.now(timezone.utc).date()
    delta = (target_date - EPOCH_START_DATE).days
    return max(0, delta)



def gita_index_to_chapter_verse(global_index: int) -> Tuple[int, int]:
    """Convert global verse index 1..700 to (chapter, verse)."""
    idx = max(1, min(global_index, TOTAL_GITA_VERSES))
    accum = 0
    for ch in range(1, 19):
        count = GITA_CHAPTER_VERSE_COUNTS[ch]
        if accum + count >= idx:
            verse = idx - accum
            return ch, verse
        accum += count
    return 18, 78


def gita_chapter_verse_to_index(chapter: int, verse: int) -> int:
    """Convert (chapter, verse) to global index 1..700."""
    ch = max(1, min(chapter, 18))
    max_v = GITA_CHAPTER_VERSE_COUNTS[ch]
    v = max(1, min(verse, max_v))
    accum = sum(GITA_CHAPTER_VERSE_COUNTS[c] for c in range(1, ch))
    return accum + v


# In-memory LRU-like cache for fetched Gita verses to make navigation lightning fast
_GITA_CACHE: Dict[str, dict] = {}


def fetch_live_gita_slok(chapter: int, verse: int) -> dict:
    """
    Fetches authentic Sanskrit, transliteration, translations, and commentaries
    directly from public Vedic Scriptures API.
    """
    cache_key = f"{chapter}_{verse}"
    if cache_key in _GITA_CACHE:
        return _GITA_CACHE[cache_key]

    url = f"https://vedicscriptures.github.io/slok/{chapter}/{verse}"
    try:
        resp = requests.get(url, timeout=4)
        if resp.status_code == 200:
            data = resp.json()
            _GITA_CACHE[cache_key] = data
            return data
    except Exception as e:
        logger.warning(f"Primary Gita API error for {chapter}.{verse}: {e}")

    # Secondary mirror attempt
    try:
        url_mirror = f"https://bhagavadgitaapi.in/slok/{chapter}/{verse}"
        resp_m = requests.get(url_mirror, timeout=4)
        if resp_m.status_code == 200:
            data = resp_m.json()
            _GITA_CACHE[cache_key] = data
            return data
    except Exception as e2:
        logger.warning(f"Secondary Gita API mirror error for {chapter}.{verse}: {e2}")

    return None


GITA_CHAPTER_DETAILED_CONTEXTS = {
    1: "The great Kurukshetra war is about to begin after 13 years of exile and the failure of all diplomatic peace missions by Shri Krishna. The vast armies of the Pandavas (7 Akshauhinis) and the Kauravas (11 Akshauhinis) stand face to face on the holy field of Kurukshetra (Dharmakshetra). Blind King Dhritarashtra, anxious in his palace at Hastinapura, asks his charioteer Sanjaya—who has been blessed with divine clairvoyance (Divya Drishti) by Sage Vyasa—to narrate the battle. As divine conches like Panchajanya and Devadatta echo across the plains, Arjuna asks Shri Krishna to drive his chariot between the two armies. Looking upon his beloved grandfather Bhishma, revered teacher Dronacharya, cousins, and friends, Arjuna's heart sinks. Overcome by grief and moral dilemma, his bow Gandiva slips from his hand, and he collapses into his chariot refusing to fight.",
    2: "Seeing Arjuna weeping and paralyzed by sorrow, Shri Krishna begins the eternal teaching of the Gita. Arjuna surrenders completely, requesting Krishna to guide him as a master to a disciple. Krishna rebukes his faint-heartedness and reveals the supreme secret of the Soul (Atman): the soul is eternal, unborn, imperishable, and unaffected by birth or death, while the body is merely like a garment changed at the end of its time. Krishna then introduces the revolutionary path of Nishkama Karma Yoga—acting with supreme excellence and dedication without being attached to results. He concludes with the portrait of the Sthitaprajna (a person of steady wisdom) who remains serene in pleasure and pain.",
    3: "Confused between renunciation of work and active duty, Arjuna asks why Krishna urges him into the fierce battle. Krishna explains Karma Yoga: no human being can remain inactive for even a fraction of a second, for nature's forces (Gunas) perpetually compel action. The secret of freedom is not running away from responsibility, but performing one's prescribed duties as an offering (Yajna) for the welfare of the world (Lokasamgraha), just as King Janaka attained liberation through selfless service. He warns that selfish desire (Kama) and anger (Krodha) are the all-devouring enemies that cloud human judgment.",
    4: "Krishna reveals that this timeless science of yoga is ancient, once taught to the Sun God (Vivasvan) at the dawn of civilization. When Arjuna wonders how Krishna could have taught Vivasvan who lived ages before, Krishna declares the mystery of divine incarnation (Avatarahood): whenever righteousness declines and unrighteousness rises, the divine manifests to protect the virtuous and restore moral order. He elucidates that true action in inaction and inaction in action is understood by the wise, and that transcendental knowledge is the ultimate purifier that burns all karmic bondage into ashes.",
    5: "Arjuna asks whether the path of renunciation (Sanyasa) or the path of dedicated action (Karma Yoga) is superior. Krishna explains that both lead to the same supreme goal of liberation, but Karma Yoga is safer, swifter, and more practical for humanity. One who performs duties without selfish attachment, surrendering all fruits to the Supreme, remains untouched by sorrow and karmic reaction, just as a lotus leaf rests on water without ever being wetted by it. Such a person sees all beings with an equal eye and attains unbroken inner peace.",
    6: "Krishna explains Dhyana Yoga (the Yoga of Meditation) and the mastery of the mind. He describes the disciplined posture, regulated diet, balanced sleep, and single-pointed concentration needed to calm mental turbulence. When Arjuna confesses that controlling the wandering mind is as difficult as holding back the rushing wind, Krishna reassures him that through persistent practice (Abhyasa) and non-attachment (Vairagya), the restless mind can definitely be mastered. He assures that no effort on the spiritual path is ever wasted, and the yogi who meditates on the Divine within is the highest of all.",
    7: "Krishna reveals Jnana-Vijnana Yoga—the comprehensive knowledge of both the manifest physical universe (Apara Prakriti) and the unmanifest spiritual source (Para Prakriti). Krishna explains that He is the essence of all things: the taste in water, the light in the sun and moon, the sacred sound OM in the Vedas, and the life-force in all beings. He explains that His divine illusion (Maya) made of the three Gunas is difficult to cross, but those who surrender wholeheartedly unto Him cross over it effortlessly.",
    8: "Responding to Arjuna's questions regarding Brahman, Adhyatma, Karma, and the mystery of death, Krishna expounds on the Imperishable Absolute (Akshara Brahma). He explains the great cosmic law: whatever state of being a person remembers at the time of departing the body, that very state they attain. Therefore, Krishna advises Arjuna to remember the Divine at all times while performing his worldly duty in battle (Mamanusmara Yudhya Cha). Those who attain the supreme abode beyond the cycle of creation and dissolution never return to the realm of suffering.",
    9: "Krishna imparts the Raja Vidya and Raja Guhya—the Sovereign Science and Sovereign Secret. He reveals that the entire universe is pervaded by Him, yet He remains unattached as the detached witness and preserver. Krishna makes the eternal compassionate promise: 'To those who are constantly devoted and worship Me with love, I personally provide what they lack and preserve what they have (Yoga-Kshema).' Even the humblest offering—a leaf, a flower, a fruit, or a drop of water—offered with pure devotion is joyfully accepted by the Divine.",
    10: "In the Vibhuti Yoga, Krishna reveals His magnificent cosmic splendors and manifestations. He explains that He is the beginning, the middle, and the end of all creations. Among the lights He is the radiant Sun; among the mountains He is Mount Meru; among the waters He is the ocean; among the trees He is the sacred Ashvattha; and among the Pandavas He is Arjuna. Whatever entity possesses extraordinary power, beauty, brilliance, or grace originates as a mere spark of His boundless divine splendor.",
    11: "Arjuna, filled with awe, prays to behold Krishna's cosmic universal form (Vishvarupa). Krishna bestows divine vision (Divya Chakshu) upon Arjuna. Arjuna beholds the boundless form of the Supreme encompassing all worlds, stars, gods, and galaxies, with thousands of eyes, faces, and celestial ornaments. Terrified by the all-devouring form of Time (Kala) devouring warriors on both sides, Arjuna bows with folded hands in awe, asking for forgiveness for ever treating Krishna as an ordinary friend, and prays for the return of His gentle four-armed form.",
    12: "Arjuna asks whether worshipping the personal form of God (Saguna Bhakti) or meditating upon the formless, unmanifest Absolute (Nirguna Upasana) is superior. Krishna explains that while the formless path is arduous for embodied beings, pure loving devotion to the personal Divine is the swiftest and sweetest path. He describes the 35 divine characteristics of a true devotee (Bhakta): free from malice, friendly and compassionate to all, free from ego and possessiveness, equal in joy and sorrow, and ever content with whatever comes unsought.",
    13: "Krishna explains the distinction between Kshetra (the Field — the human body, mind, senses, and material world) and Kshetrajna (the Knower of the Field — the pure conscious Soul). He describes the 20 virtues that constitute true wisdom: humility, non-violence, patience, uprightness, service to the teacher, purity, steadfastness, and freedom from egotism. One who perceives the same imperishable Supreme Lord dwelling equally in all perishable living beings possesses true vision and never degrades themselves.",
    14: "Krishna reveals the profound operation of the Three Gunas of material nature: Sattva (purity, harmony, knowledge), Rajas (passion, restless desire, aggressive activity), and Tamas (inertia, darkness, delusion). These three ropes bind the soul to physical embodiment. Krishna explains how each Guna influences human behavior, diet, and spiritual evolution, and describes the Gunatita—the liberated master who has transcended all three Gunas and remains a calm witness through the play of nature.",
    15: "Krishna uses the majestic metaphor of the cosmic Ashvattha tree with roots above in the unmanifest realm and branches spreading downward in the material world, which must be cut down with the sharp axe of non-attachment. He distinguishes between the Perishable (Kshara — physical bodies), the Imperishable (Akshara — eternal souls), and the Supreme Divine Person (Purushottama — the Lord who sustains the three worlds). Knowing this Purushottama Yoga brings ultimate fulfillment to human intellect.",
    16: "Krishna delineates the Daivasura Sampad—the division between Divine (Daivi) and Demonic (Asuri) qualities. Divine virtues include fearlessness, purity of heart, steadfastness in knowledge, charity, restraint, harmlessness, truth, and forgiveness, which lead to freedom. Demonic traits like arrogance, anger, harshness, conceit, and insatiable greed lead to bondage and self-destruction. He identifies the three gates to hell that ruin the soul: Lust (Kama), Anger (Krodha), and Greed (Lobha), advising seekers to renounce them completely.",
    17: "Arjuna inquires about people who perform worship with deep faith (Shraddha), but without following strict scriptural rituals. Krishna explains the Threefold Division of Faith based on the Gunas: Sattvic faith seeks truth and selfless service, Rajasic faith seeks personal power and praise, and Tamasic faith is steeped in ignorance. He classifies food, sacrifice (Yajna), austerity (Tapas), and charity (Dana) into the three Gunas, explaining the purifying spiritual power of the sacred formula 'OM TAT SAT'.",
    18: "In the monumental final chapter, Krishna synthesizes the entire teachings of the Vedas. He clarifies the distinction between Tyaga (relinquishing the selfish fruits of action) and Sanyasa (renunciation of desire-prompted actions), establishing that duties of charity, sacrifice, and duty must never be abandoned. He leads Arjuna through the heights of wisdom and concludes with the supreme secret of absolute surrender: 'Abandon all varieties of dharmas and simply surrender unto Me alone; I shall liberate you from all sins, do not grieve.' Arjuna's doubts vanish, and with clear resolve he takes up his bow Gandiva to fulfill his duty."
}


def get_gita_reflection_details(chapter: int, verse: int, translation: str) -> dict:
    """
    Generates insightful context, life takeaways, and practices based on
    the chapter philosophy and verse theme (deterministic, no AI needed).
    """
    ch_info = GITA_CHAPTER_NAMES.get(chapter, {
        "name": f"Chapter {chapter}",
        "sanskrit": "",
        "summary": "The path of self-knowledge and righteousness"
    })

    title = f"{ch_info['name']} — Verse {verse}"
    story_context = GITA_CHAPTER_DETAILED_CONTEXTS.get(
        chapter,
        f"In Chapter {chapter} ({ch_info['name']} — {ch_info['sanskrit']}), "
        f"on the sacred battlefield of Kurukshetra, Shri Krishna addresses Arjuna's "
        f"deepest human doubts. {ch_info['summary']}."
    )

    explanation = (
        f"{translation}\n\n"
        f"This verse reveals an essential truth from {ch_info['name']}. "
        f"Krishna guides the seeker from confusion to clarity by shifting the focus "
        f"from external anxiety to inner mastery and selfless action. "
        f"When we align our mind with duty (Dharma) and let go of obsessive attachment "
        f"to rewards, we experience profound peace and invincible mental focus."
    )

    key_takeaways = [
        f"Establish clarity of purpose in {ch_info['name']}'s wisdom",
        "Focus completely on the excellence of your effort rather than anxiety over results",
        "Maintain inner poise in both success and adversity",
        "Transform daily work into a joyful spiritual discipline"
    ]

    today_practice = {
        "title": "Living with Single-Minded Focus (Vyavasayatmika Buddhi)",
        "description": f"Today, choose one key responsibility. Approach it with complete presence of mind and devotion, dedicating the fruit of your labor to the greater good."
    }

    journal_prompt = (
        f"Reflect on Bhagavad Gita {chapter}.{verse}: How can you apply this teaching "
        f"to resolve a current dilemma, calm an anxious thought, or elevate your daily focus?"
    )

    return {
        "title": title,
        "story_context": story_context,
        "explanation": explanation,
        "key_takeaways": key_takeaways,
        "today_practice": today_practice,
        "journal_prompt": journal_prompt
    }



def get_gita_lesson(
    day: Optional[int] = None,
    chapter: Optional[int] = None,
    verse: Optional[int] = None,
    target_date_str: Optional[str] = None
) -> dict:
    """Builds a complete, authentic Bhagavad Gita lesson for a given day or chapter/verse."""
    if not target_date_str:
        target_date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    if chapter is not None and verse is not None:
        ch = max(1, min(chapter, 18))
        max_v = GITA_CHAPTER_VERSE_COUNTS[ch]
        v = max(1, min(verse, max_v))
        day_num = gita_chapter_verse_to_index(ch, v)
    elif day is not None:
        day_num = ((day - 1) % TOTAL_GITA_VERSES) + 1
        ch, v = gita_index_to_chapter_verse(day_num)
    else:
        offset = get_day_offset()
        day_num = (offset % TOTAL_GITA_VERSES) + 1
        ch, v = gita_index_to_chapter_verse(day_num)

    api_data = fetch_live_gita_slok(ch, v)

    if api_data:
        sanskrit = api_data.get("slok") or ""
        transliteration = api_data.get("transliteration") or ""
        
        # Priority for clear, beautiful English translations
        translation = (
            (api_data.get("siva") or {}).get("et") or
            (api_data.get("purohit") or {}).get("et") or
            (api_data.get("tej") or {}).get("ec") or
            (api_data.get("gambir") or {}).get("et") or
            f"Chapter {ch}, Verse {v} of the Bhagavad Gita."
        ).strip()

        # Hindi translation
        hindi_translation = (
            (api_data.get("tej") or {}).get("ht") or
            (api_data.get("rams") or {}).get("ht") or
            (api_data.get("chinmay") or {}).get("hc") or
            "धृतराष्ट्र ने कहा -- हे संजय ! धर्मभूमि कुरुक्षेत्र में एकत्र हुए युद्ध के इच्छुक मेरे और पाण्डु के पुत्रों ने क्या किया?"
        ).strip()

        # Collect rich commentaries
        commentators = {}
        if (api_data.get("siva") or {}).get("et"):
            commentators["Swami Sivananda"] = api_data["siva"]["et"].strip()
        if (api_data.get("purohit") or {}).get("et"):
            commentators["Purohit Swami"] = api_data["purohit"]["et"].strip()
        if (api_data.get("chinmay") or {}).get("hc"):
            commentators["Swami Chinmayananda"] = api_data["chinmay"]["hc"].strip()
        if (api_data.get("gambir") or {}).get("et"):
            commentators["Swami Gambhirananda"] = api_data["gambir"]["et"].strip()
        if (api_data.get("raman") or {}).get("et"):
            commentators["Sri Ramanuja"] = api_data["raman"]["et"].strip()
        if (api_data.get("sankar") or {}).get("et"):
            commentators["Adi Shankaracharya"] = api_data["sankar"]["et"].strip()
    else:
        # High quality offline fallback
        sanskrit = "कर्मण्येवाधिकारस्ते मा फलेषु कदाचन।\nमा कर्मफलहेतुर्भूर्मा ते सङ्गोऽस्त्वकर्मणि॥" if (ch == 2 and v == 47) else "धर्मक्षेत्रे कुरुक्षेत्रे समवेता युयुत्सवः।\nमामकाः पाण्डवाश्चैव किमकुर्वत सञ्जय॥"
        transliteration = "karmaṇyevādhikāraste mā phaleṣu kadācana |\nmā karmaphalaheturbhūrmā te saṅgo'stvakarmaṇi ||" if (ch == 2 and v == 47) else "dharmakṣetre kurukṣetre samavetā yuyutsavaḥ |\nmāmakāḥ pāṇḍavāścaiva kimakurvata sañjaya ||"
        translation = (
            "You have a right to perform your prescribed duties, but you are not entitled to the fruits of your actions. "
            "Never consider yourself to be the cause of the results of your activities, nor be attached to inaction."
            if (ch == 2 and v == 47) else
            "Dhritarashtra said: O Sanjaya, assembled on the holy field of Kurukshetra and eager for battle, what did my sons and the sons of Pandu do?"
        )
        hindi_translation = (
            "तुम्हारा अधिकार केवल कर्म करने में है, फल में कभी नहीं। इसलिए तुम कर्मफल के हेतु मत बनो और न ही अकर्मण्यता में तुम्हारी आसक्ति हो।"
            if (ch == 2 and v == 47) else
            "धृतराष्ट्र ने कहा: हे संजय! धर्मभूमि कुरुक्षेत्र में युद्ध की इच्छा से इकट्ठे हुए मेरे और पाण्डु के पुत्रों ने क्या किया?"
        )
        commentators = {
            "Swami Sivananda": "Action without desire for the fruit brings purification of the mind and liberation.",
            "Swami Mukundananda": "Do your duty with full devotion; surrender the results to God."
        }

    reflection = get_gita_reflection_details(ch, v, translation)

    return {
        "lesson_date": target_date_str,
        "day_number": day_num,
        "total_days_or_verses": TOTAL_GITA_VERSES,
        "topic": GITA_CHAPTER_NAMES.get(ch, {}).get("name", f"Chapter {ch}"),
        "source": {
            "name": "Bhagavad Gita",
            "scripture_type": "gita",
            "reference": f"Bhagavad Gita {ch}.{v}",
            "chapter": ch,
            "verse": v,
            "kanda_or_parva": f"Chapter {ch}",
            "character": "Shri Krishna" if ch > 1 or v >= 25 else "Sanjaya / Arjuna",
            "original_sanskrit": sanskrit,
            "transliteration": transliteration,
            "translation": translation,
            "hindi_translation": hindi_translation,
            "commentators": commentators
        },
        "reflection": {
            "title": reflection["title"],
            "story_context": reflection["story_context"],
            "explanation": reflection["explanation"],
            "key_takeaways": reflection["key_takeaways"]
        },
        "today_practice": reflection["today_practice"],
        "journal_prompt": reflection["journal_prompt"]
    }

MYTHOLOGICAL_CHARACTERS = [
    "Brahma",
    "Vishnu",
    "Shiva",
    "Saraswati",
    "Lakshmi",
    "Parvati",
    "Matsya",
    "Kurma",
    "Varaha",
    "Narasimha",
    "Vamana",
    "Parashurama",
    "Rama",
    "Krishna",
    "Balarama",
    "Kalki",
    "Shailaputri",
    "Brahmacharini",
    "Chandraghanta",
    "Kushmanda",
    "Skandamata",
    "Katyayani",
    "Kalaratri",
    "Mahagauri",
    "Siddhidhatri",
    "Kali",
    "Tara (Devi)",
    "Tripura Sundari",
    "Bhuvaneshvari",
    "Bhairavi",
    "Chhinnamasta",
    "Dhumavati",
    "Bagalamukhi",
    "Matangi",
    "Kamala (goddess)",
    "Yudhishthira",
    "Bhima",
    "Arjuna",
    "Nakula",
    "Sahadeva",
    "Draupadi",
    "Duryodhana",
    "Dushasana",
    "Karna",
    "Bhishma",
    "Drona",
    "Ashwatthama",
    "Shakuni",
    "Dasharatha",
    "Sita",
    "Lakshmana",
    "Bharata (Ramayana)",
    "Shatrughna",
    "Hanuman",
    "Sugriva",
    "Vibhishana",
    "Ravana",
    "Kumbhakarna",
    "Indrajit",
    "Hiranyakashipu",
    "Hiranyaksha",
    "Mahishasura",
    "Holika",
    "Bhasmasura",
    "Raktabīja",
    "Indra",
    "Agni",
    "Surya",
    "Vayu",
    "Varuna",
    "Yama",
    "Soma",
    "Kubera",
    "Dattatreya",
    "Dhisana",
    "Satyavati",
    "Gayatri",
    "Aniruddha",
    "Dharā",
    "Muchilot Bhagavathi",
    "Dhritarashtra",
    "Apsara",
    "Akampana",
    "Nandi (Hinduism)",
    "Vikarna",
    "Virata",
    "Sumali",
    "Hidimbi",
    "Sang Hyang Widhi Wasa",
    "Namuchi",
    "Jivdani Mata",
    "Shakuntala",
    "Śvetaketu",
    "Jagannath",
    "Kamadeva",
    "Khodiyar",
    "Parikshit",
    "Vishrava",
    "Trijata",
    "Prasuti",
    "Ranganayaki",
    "Balambika",
    "Bhagadatta",
    "Maa Tarini",
    "Sushena",
    "Angada (Lakshmana's son)",
    "Kritavarma",
    "Akrura",
    "Budha",
    "Rudrani",
    "Pretakshi Devi",
    "Prachetas",
    "Mandavi",
    "Subahu (Shatrughna's son)",
    "Kamakhya",
    "Prahasta",
    "Kannagi",
    "Vrishaketu",
    "Shalya",
    "Ashokasundari",
    "Kartavirya Arjuna",
    "Kubjika",
    "Brahmani (Matrika)",
    "Ammavaru",
    "Ahmuvan",
    "Pancha Prakriti (Five Goddesses)",
    "Rishyasringa",
    "Atikaya",
    "Kalmashapada",
    "Vrishakapi",
    "Kamaksha",
    "Ambalika",
    "Tridevi",
    "Yogeshvari",
    "Kaushiki",
    "Rudrasundari",
    "Puru (legendary king)",
    "Pashupati",
    "Wives of Duryodhana",
    "Badi Mata",
    "Ahalya",
    "Tvarita",
    "Ashapura Mata",
    "Tara (Mahavidya)",
    "Kamadhenu",
    "Tara (Hindu goddess)",
    "Damayanti",
    "Gandhari",
    "Ashta Lakshmi",
    "Jaganmata",
    "Aranyani",
    "Vedavati",
    "Uttamaujas and Yudhamanyu",
    "Kaunteya",
    "Sandipani",
    "Tara (Ramayana)",
    "Nara-Narayana",
    "Ratri",
    "Yogamaya",
    "Ilavida",
    "Ganga (goddess)",
    "Shantadurga",
    "Vakula Devi",
    "Uttara (Mahabharata)",
    "Tapati",
    "Banka-Mundi",
    "Brihadratha",
    "Virabhadra",
    "Dhata",
    "Dharmathakur",
    "Romapada",
    "Madhavi (princess)",
    "Dvivida",
    "Khemukhi",
    "Ekanamsha",
    "Shishupala",
    "Temblai",
    "Brihannala",
    "Durvasa",
    "Bahlika (king)",
    "Iravati",
    "Vyasa",
    "Maṇibhadra",
    "Sharabha",
    "Harsidhhi",
    "Takshaka",
    "Vinda and Anuvinda of Avanti",
    "Devaki",
    "Priti (goddess)",
    "Parjanya (Hinduism)",
    "Danu (Hinduism)",
    "Markandeya",
    "Samvarana",
    "Vishvavasu",
    "Harishchandra",
    "Nikumbha",
    "Ahilawati",
    "Lakshmi Chandralamba Parameshwari",
    "Ugrashravas",
    "Shivaduti",
    "Aditi",
    "Madravati",
    "Puloma",
    "Neela (goddess)",
    "Tilottama",
    "Rohini (wife of Vasudeva)",
    "Subahu",
    "Yogini",
    "Astika (sage)",
    "Hansa and Dimbhaka",
    "Indrani",
    "Mārtanda",
    "Parnashavari",
    "Kushadhvaja",
    "Bahuchara Mata",
    "Apam Napat",
    "Bhumi (goddess)",
    "Satyaki",
    "Atithi (Ramayana)",
    "Angala Devi",
    "Kotavi",
    "Divodasa",
    "Madreya",
    "Vrihanta",
    "Chelamma",
    "Agneya",
    "Jyoti (goddess)",
    "Vrinda (goddess)",
    "Yayati",
    "Wives of Karna",
    "Kavyamata",
    "Kecaikhati",
    "Prajapati",
    "Devapi",
    "Jaratkaru",
    "Vajreshvari Devi",
    "Śarabhanga",
    "Guha (Ramayana)",
    "Somalamma",
    "Amshuman",
    "Sri Ramalinga Sowdeswari Amman",
    "Alakshmi",
    "Jayadurgā",
    "Parjanya",
    "Rati",
    "Hidimba",
    "Kindama",
    "Urmila",
    "Maruts",
    "Māṇḍakarṇi",
    "Budhi Pallien",
    "Urvashi",
    "Nagalakshmi",
    "Boyakonda Gangamma",
    "Sarvamangala temple",
    "Manasa",
    "Deva (Hinduism)",
    "Khyati",
    "Sunayana (Ramayana)",
    "Jwala (goddess)",
    "Kalayavana",
    "Vasudeva",
    "Jabali",
    "Sahadeva of Magadha",
    "Kaikashi",
    "Amba (Mahabharata)",
    "Aja of Kosala",
    "Chhaya",
    "Para Brahman",
    "Mātali",
    "Rukmini",
    "Modheshwari",
    "Dewi Ratih",
    "Maalikapurathamma",
    "Abhimanyu",
    "Krodhavasa",
    "Devasena",
    "Chitrangada (princess)",
    "Karumariamman",
    "Harihara",
    "Ilvala and Vatapi",
    "Jayanti (Hinduism)",
    "Bhagavati",
    "Visalakshi",
    "Bhumanyu",
    "Sarama",
    "Bhutamata",
    "Mahakala",
    "Garuda",
    "Narakasura",
    "Uttamabhadras",
    "Bala Tripurasundari",
    "Susharma",
    "Jambavan",
    "Shambuka",
    "Varahi",
    "Sanjaya",
    "Gādhi",
    "Swasthani Barta (Fast)",
    "Vijayadurga",
    "Mandavya",
    "Bhagiratha",
    "Ishvari",
    "Lomasha",
    "Menaka",
    "Phul Mata",
    "Lairai",
    "Ushas",
    "Chenjiamman",
    "Chandrahasa",
    "Padmavati (Hinduism)",
    "Vinayaki",
    "Pratipa",
    "Ugrasena",
    "Ila (Hinduism)",
    "Asikni (goddess)",
    "Mookambika",
    "Indradyumna",
    "Shanta",
    "Nalakuvara",
    "Ashtabharya",
    "Satrajit",
    "Archi (Hindu goddess)",
    "Mahadevi",
    "Chitragupta",
    "Nahusha",
    "Suswani Mataji",
    "Amsha",
    "Pulastya",
    "Lakshmana (Mahabharata)",
    "Anaranya",
    "Poleramma",
    "Kamatha",
    "Rituparna",
    "Pradyumna",
    "Dhrishtaketu",
    "Manikeswari",
    "Bhaga",
    "Bhadra",
    "Ambarisha",
    "Dushyanta",
    "Panchakanya",
    "Pushan",
    "Bhurishravas",
    "Kusha (Ramayana)",
    "Gautama Maharishi",
    "Vajreshwari Temple",
    "Shashthi",
    "Lajja Gauri",
    "Muthyalamma",
    "Viprachitti",
    "Kaikeyi",
    "Pratyangira",
    "Meldi Mata",
    "Maisamma",
    "Bharata (Mahabharata)",
    "Ashvapati",
    "Vinata",
    "Nandipada",
    "Svaha",
    "Ekalavya",
    "Shakambhari",
    "Rukmi",
    "Narayana",
    "Consorts of Ganesha",
    "Anumati (deity)",
    "Drupada",
    "Korravai",
    "Rudras",
    "Vāc",
    "Lava (Ramayana)",
    "Trideva",
    "Radha",
    "Mahakali",
    "Ghatotkacha",
    "Bhagamalini",
    "Nandagopa",
    "Rahu",
    "Thirty-three gods",
    "Rudra",
    "Ambika (Mahabharata)",
    "Pushkara",
    "Revati",
    "Niladevi",
    "Anasuya",
    "Pandu",
    "Saat Behna (Seven Sisters goddesses)",
    "Naigamesha",
    "Putana",
    "Kaliya",
    "Chitraratha",
    "Akilandeswari",
    "Sanjna",
    "Dev Mogra",
    "Sumitra",
    "Nagnechiya Mata",
    "Purochana",
    "Vandin",
    "Prithvi",
    "Akshayakumara",
    "Vrishasena",
    "Uttanka",
    "Asamanja",
    "Vidura",
    "Santoshi Mata",
    "Prapaksha Kamboja",
    "Kamalatmika",
    "Pururavas",
    "Samba (Krishna's son)",
    "Shurasena",
    "Sudakshina",
    "Raktadantika",
    "Dhrishtadyumna",
    "Kunti",
    "Bhishmaka",
    "Uddālaka Āruṇi",
    "Yuyutsu",
    "Rohini (nakshatra)",
    "Revanta",
    "Kateri Amman",
    "Vershini",
    "Shani",
    "Vasishtha",
    "Tvashtr",
    "Bambar Baini",
    "Acintya",
    "Dantavakra",
    "Uttarā",
    "Ikshvaku",
    "Subhadra",
    "Jagdamba",
    "Sampati",
    "Shibi (king)",
    "Jayadratha",
    "Jagaddhatri",
    "Shrutayudha",
    "Asvayujau",
    "Aruna (Hinduism)",
    "Chandra",
    "Annapurna (goddess)",
    "Rambha (apsara)",
    "Yaksha",
    "Diti",
    "Tumburu",
    "Chandraketu",
    "Renuka",
    "Lankini",
    "Satyabhama",
    "Aryaman",
    "Chitrasena (gandharva)",
    "Nirṛti",
    "Yadu (legendary king)",
    "Dushala",
    "Vajradatta",
    "Ishana",
    "Ghritachi",
    "Shakti",
    "Vishvakarma",
    "Dhaumya",
    "Iravan",
    "Dewi Sri",
    "Rakteswari",
    "Dhanvantari",
    "Trimurti",
    "Vichitravirya",
    "Mayasura",
    "Uparichara Vasu",
    "Vaisampayana",
    "Bharat Mata",
    "Masani Amman",
    "Rantideva",
    "Sati (Hindu goddess)",
    "Uluka",
    "Vishala",
    "Madri",
    "Kolaramma",
    "Ganesha",
    "Mitra (Hindu god)",
    "Dilīpa",
    "Sulochana (wife of Indrajit)",
    "Hemadryamba",
    "Bhadrakali",
    "Valli",
    "Periyachi",
    "Himavat",
    "Kakudmi",
    "Kshetrapala",
    "Sinivali",
    "Jatayu",
    "Nandni Mata",
    "Kaurava",
    "Lomaharshana",
    "Devi Kanya Kumari",
    "Yashoda",
    "Shesha",
    "Devi",
    "Batuka Bhairava",
    "Suvannamaccha",
    "Makaradhwaja",
    "Jyestha (goddess)",
    "Maitreya (Mahābhārata)",
    "Janaka",
    "Vishvaksena",
    "Muchukunda",
    "Devayani",
    "Mitra–Varuna",
    "Nala",
    "Anila",
    "Kripa",
    "Mukasura",
    "Kushanabha",
    "Jayatsena",
    "Babhruvahana",
    "Mohini",
    "Guardians of the directions",
    "Banjari (deity)",
    "Taleju Bhawani",
    "Kumari (goddess)",
    "Sunaka",
    "Karni Mata",
    "Virabahu",
    "Chandi",
    "Jarasandha",
    "Bhramari",
    "Shrutakirti",
    "Ulupi",
    "Vipattāriṇī Dēvī",
    "Madayi Kavu",
    "Ashvins",
    "Manthara",
    "Surasa",
    "Rumā",
    "Shantanu",
    "Draupadeyas",
    "Mhalsa",
    "Savitri and Satyavan",
    "Jayanta",
    "Ashvatthama",
    "Sharmishtha",
    "Kacha (sage)",
    "Pratardana",
    "Ambika (goddess)",
    "Varuni",
    "Ribhus",
    "Kamsa",
    "Maya Sita",
    "Janamejaya",
    "Dharmabhrit",
    "Kaushalya",
    "Navadurga",
    "Vaishno Devi",
    "Kartikeya",
    "Nilakanta (Hinduism)",
    "Usha (princess)",
    "Lavanasura",
    "Mahavidya",
    "Harishankari",
    "Kichaka",
    "Shaunaka",
    "Chitrangada (king)",
    "Brihadbala",
    "Jhandewali Mata",
    "Matrikas",
    "Simhika",
    "Bhavani",
    "Kurupuram",
    "Kalanemi",
    "Ram Ki Shakti Puja",
    "Bharadvaja",
    "Sudeshna",
    "Brihaspati",
    "Durga",
    "Banaasura",
    "Dewi Danu"
]

def fetch_wikipedia_extract(character: str) -> Optional[dict]:
    """Fetches and caches the Wikipedia extract and image for a mythological character."""
    if character in _CHARACTER_CACHE:
        return _CHARACTER_CACHE[character]

    url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "prop": "extracts|pageprops|pageimages",
        "pithumbsize": "800",
        "explaintext": "1",
        "titles": character,
        "redirects": "1",
        "formatversion": "2",
        "format": "json"
    }
    headers = {"User-Agent": "10xDailyApp/1.0 (https://10xdaily.com; contact@10xdaily.com)"}
    
    result = None
    # Try fetching with 1 retry
    for attempt in range(2):
        try:
            resp = requests.get(url, params=params, headers=headers, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            pages = data.get("query", {}).get("pages", [])
            if pages and not pages[0].get("missing"):
                page = pages[0]
                # Skip disambiguation pages
                if "disambiguation" in page.get("pageprops", {}):
                    logger.warning(f"Wikipedia page for {character} is a disambiguation page.")
                    break
                extract = page.get("extract")
                image_url = page.get("thumbnail", {}).get("source")
                if extract:
                    result = {"extract": extract, "image_url": image_url}
                    _CHARACTER_CACHE[character] = result
                    break
        except requests.RequestException as e:
            logger.warning(f"Attempt {attempt+1} failed to fetch Wikipedia data for {character}: {e}")
            
    return result

def get_character_lesson(day: Optional[int] = None, target_date_str: Optional[str] = None) -> dict:
    """Builds a daily lesson based on a mythological character from Wikipedia."""
    if not target_date_str:
        target_date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    total_items = len(MYTHOLOGICAL_CHARACTERS)
    if day is not None:
        day_num = ((day - 1) % total_items) + 1
    else:
        offset = get_day_offset()
        day_num = (offset % total_items) + 1

    character = MYTHOLOGICAL_CHARACTERS[day_num - 1]
    
    # Fetch from Wikipedia API (cached)
    wiki_data = fetch_wikipedia_extract(character)
    
    import re

    extract = wiki_data.get("extract") if wiki_data else None
    image_url = wiki_data.get("image_url") if wiki_data else None

    if not extract:
        extract = f"{character} is a significant figure in Hindu mythology. We are currently gathering more detailed information from our sources."
        explanation = extract
        facts = [f"Explore more about the legend of {character}."]
        story_context = ""
        practice = f"Take a moment to reflect upon the values associated with {character}."
        prompt = f"What lessons can you draw from the mythology of {character}?"
    else:
        # Strip out useless sections like References, See also, External links
        clean_text = re.split(r'==\s*(?:See also|References|Notes|Further reading|External links|Gallery)\s*==', extract, flags=re.IGNORECASE)[0].strip()
        
        # Separate intro from the rest of the body
        parts = re.split(r'\n==', clean_text, 1)
        intro_text = parts[0].strip()
        
        body_text = '==' + parts[1] if len(parts) > 1 else ""
        
        # Escape body HTML to prevent XSS from Wikipedia artifacts before we inject our own tags
        body_text = html.escape(body_text)
        
        # Format the body text into HTML headings for colored topics and subtopics
        def format_heading(m):
            level = len(m.group(1))
            text = m.group(2).strip().upper()
            if level == 2:
                return f'<h3 class="story-topic">{text}</h3>'
            else:
                return f'<h4 class="story-subtopic">{text}</h4>'
                
        story_context = re.sub(r'^(=+)\s*(.*?)\s*\1$', format_heading, body_text, flags=re.MULTILINE).strip()
        
        # Collapse massive whitespace gaps (including spaces between newlines) into clean paragraph breaks
        story_context = re.sub(r'(\n\s*){2,}', '\n\n', story_context)
        
        # Format newlines around HTML headings so CSS margins render properly with pre-wrap
        story_context = re.sub(r'\n*<h', '\n\n<h', story_context)
        story_context = re.sub(r'</h(\d)>\n*', r'</h\1>\n', story_context)
        story_context = story_context.strip()
        
        # Clean up linguistic metadata in the intro to make it highly readable
        cleaned_intro = re.sub(r'\s*\([^)]*(?:Sanskrit:|IAST:|pronounced|lit\.|also spelled)[^)]*\)', '', intro_text)
        cleaned_intro = re.sub(r'\s*\[[^\]]+\]', '', cleaned_intro)
        cleaned_intro = re.sub(r'\s*\(\s*[;,\s]*\)', '', cleaned_intro)
        cleaned_intro = re.sub(r',\s*,', ',', cleaned_intro)
        cleaned_intro = re.sub(r'\s+,', ',', cleaned_intro)
        cleaned_intro = re.sub(r'\.\s*,', '.', cleaned_intro).strip()
        
        # Extract explanation and facts from intro
        sentences = [s.strip() for s in re.split(r'(?<=[.!?]) +', cleaned_intro) if s.strip()]
        if len(sentences) > 2:
            explanation = " ".join(sentences[:2])
            facts = [f"Did you know? {s}" for s in sentences[2:5]]
        else:
            explanation = intro_text
            facts = [f"Learn from the life and stories of {character}."]
            
        practice = f"Take a moment to read and reflect upon the values and stories associated with {character}."
        prompt = f"What lessons can you draw from the mythology of {character}?"

    if day_num <= 3:
        theme = "The Trimurti"
    elif day_num <= 6:
        theme = "The Tridevi"
    elif day_num <= 16:
        theme = "Dashavatara: 10 Avatars of Vishnu"
    elif day_num <= 25:
        theme = "Navadurga: 9 Forms of Durga"
    elif day_num <= 35:
        theme = "The Mahavidyas"
    elif day_num <= 41:
        theme = "The Pandavas"
    elif day_num <= 48:
        theme = "Mahabharata Legends"
    elif day_num <= 59:
        theme = "Ramayana Epics"
    elif day_num <= 65:
        theme = "The Great Asuras"
    elif day_num <= 73:
        theme = "Vedic Deities"
    else:
        theme = "Mythological Figures"

    topic = f"{theme} - Character of the Day"

    return {
        "lesson_date": target_date_str,
        "day_number": day_num,
        "total_days_or_verses": total_items,
        "topic": topic,
        "source": {
            "name": "Wikipedia",
            "scripture_type": "character",
            "reference": character,
            "chapter": None,
            "verse": None,
            "kanda_or_parva": None,
            "character": character,
            "original_sanskrit": None,
            "transliteration": None,
            "translation": explanation,
            "hindi_translation": None,
            "image_url": image_url,
            "commentators": {}
        },
        "reflection": {
            "title": f"Who is {character}?",
            "story_context": story_context,
            "explanation": explanation,
            "key_takeaways": facts
        },
        "today_practice": {
            "title": "Reflect on Character",
            "description": practice
        },
        "journal_prompt": prompt
    }


def get_daily_spiritual_lesson(
    scripture: str = "gita",
    day: Optional[int] = None,
    chapter: Optional[int] = None,
    verse: Optional[int] = None
) -> dict:
    """
    Main dispatch function: returns sequential authentic lessons from
    Gita or Character of the day.
    """
    sc = (scripture or "gita").lower().strip()
    if sc == "character":
        return get_character_lesson(day=day)
    else:
        return get_gita_lesson(day=day, chapter=chapter, verse=verse)
