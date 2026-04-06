"""
⚙️ الإعدادات المركزية للبوت
Central Configuration Module
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from typing import List, Dict, Set

load_dotenv()

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / os.getenv("DATA_DIR", "data/files")
DB_PATH = BASE_DIR / os.getenv("DB_PATH", "data/db/iraq_data.db")
LOG_DIR = BASE_DIR / "logs"

DATA_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH.parent.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN غير موجود في ملف .env")

_admin_ids_str = os.getenv("ADMIN_IDS", "")
ADMIN_IDS: List[int] = [
    int(x.strip()) for x in _admin_ids_str.split(",") if x.strip().isdigit()
]

MAX_RESULTS_PER_SEARCH: int = int(os.getenv("MAX_RESULTS", "10"))
DAILY_SEARCH_LIMIT: int = int(os.getenv("DAILY_LIMIT", "100"))
FUZZY_THRESHOLD: int = 75
CACHE_SIZE: int = int(os.getenv("CACHE_SIZE", "1000"))
CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "1000"))

SUPPORTED_EXTENSIONS: Set[str] = {
    ".csv", ".xlsx", ".xls", ".json", ".sqlite", ".db", ".accdb", ".mdb"
}

FIELD_MAPPINGS: Dict[str, List[str]] = {
    "full_name": [
        "الاسم الكامل", "الاسم", "اسم", "name", "full_name", "fullname",
        "اسم_كامل", "الاسم الرباعي", "الاسم الثلاثي", "customer_name", "مستخدم", "المواطن"
    ],
    "national_id": [
        "رقم الهوية", "هوية", "رقم هوية", "الهوية الوطنية", "national_id",
        "id_number", "id", "رقم_هوية", "الرقم الوطني", "رقم_وطني",
        "بطاقة الهوية", "رقم البطاقة"
    ],
    "province": [
        "المحافظة", "محافظة", "province", "governorate", "city",
        "مدينة", "المدينة", "المنطقة", "منطقة", "region"
    ],
    "birth_date": [
        "تاريخ ال��لادة", "ولادة", "تاريخ_الولادة", "birth_date",
        "dob", "date_of_birth", "birthdate", "سنة الولادة"
    ],
    "phone": [
        "رقم الهاتف", "هاتف", "جوال", "موبايل", "phone", "mobile",
        "phone_number", "tel", "telephone", "رقم_هاتف", "رقم_الجوال"
    ],
    "address": [
        "العنوان", "عنوان", "address", "location", "موقع",
        "السكن", "مكان السكن", "العنوان التفصيلي"
    ],
    "gender": ["الجنس", "جنس", "gender", "sex", "النوع", "نوع"],
    "nationality": ["الجنسية", "جنسية", "nationality", "country", "دولة", "البلد"],
    "email": ["البريد الإلكتروني", "ايميل", "بريد", "email", "e_mail", "mail"],
    "birth_year": ["سنة الولادة", "year_of_birth", "birth_year", "عام الولادة"],
}

IRAQ_PROVINCES = [
    "بغداد", "البصرة", "نينوى", "أربيل", "النجف", "كربلاء",
    "الأنبار", "ديالى", "بابل", "واسط", "ذي قار", "المثنى",
    "القادسية", "صلاح الدين", "كركوك", "السليمانية", "دهوك",
    "ميسان", "الموصل", "تكريت", "الفلوجة", "الناصرية"
]

MAINTENANCE_MODE: bool = os.getenv("MAINTENANCE_MODE", "false").lower() == "true"
BOT_LANG: str = os.getenv("BOT_LANG", "ar")
LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
MAX_FILE_SIZE_MB: int = 50
MAX_FILE_SIZE_BYTES: int = MAX_FILE_SIZE_MB * 1024 * 1024

MESSAGES = {
    "maintenance": "🔧 النظام في وضع الصيانة حالياً، يرجى المحاولة لاحقاً.",
    "no_permission": "⛔ ليس لديك صلاحية لتنفيذ هذه العملية.",
    "limit_exceeded": "⚠️ لقد تجاوزت الحد اليومي للبحث ({limit} بحث/يوم).",
    "no_results": "🔍 لم يتم العثور على نتائج مطابقة.",
    "error_occurred": "❌ حدث خطأ في النظام، يرجى المحاولة لاحقاً.",
    "file_processing": "⏳ جارٍ معالجة الملف وفهرسته...",
    "index_complete": "✅ تم فهرسة الملف بنجاح!\n📊 {count} سجل في {time:.2f} ثانية",
}
