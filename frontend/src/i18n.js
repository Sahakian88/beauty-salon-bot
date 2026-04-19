/**
 * Internationalization (i18n) for the Beauty Salon Mini-App.
 * Supports: Armenian (hy), Russian (ru), English (en).
 */

export const translations = {
  // ── Home Screen ──
  'home.title': { hy: 'Բարի գալուստ', ru: 'Добро пожаловать', en: 'Welcome' },
  'home.book': { hy: 'Գրանցվել', ru: 'Записаться', en: 'Book Appointment' },
  'home.book.desc': { hy: 'Ընտրեք ծառայությունը, օրը և ժամը', ru: 'Выберите услугу, дату и время', en: 'Choose a service, date & time' },
  'home.appointments': { hy: 'Իմ գրանցումները', ru: 'Мои записи', en: 'My Appointments' },
  'home.appointments.desc': { hy: 'Դիտել առաջիկա այցերը', ru: 'Просмотр предстоящих визитов', en: 'View your upcoming visits' },
  'home.admin': { hy: 'Ադմին պանել', ru: 'Админ панель', en: 'Admin Panel' },
  'home.admin.desc': { hy: 'Կառավարել ժամանակացույցը', ru: 'Управление расписанием', en: 'Manage the schedule' },
  'nav.back': { hy: 'Հետ', ru: 'Назад', en: 'Back' },
  'appointments.title': { hy: 'Իմ գրանցումները', ru: 'Мои записи', en: 'My Appointments' },
  'appointments.empty': { hy: 'Դուք դեռ գրանցումներ չունեք', ru: 'У вас пока нет записей', en: 'You have no upcoming appointments' },
  'appointments.empty.cta': { hy: 'Գրանցվել հիմա', ru: 'Записаться сейчас', en: 'Book now' },
  'appointments.cancel': { hy: 'Չեղարկել', ru: 'Отменить', en: 'Cancel' },
  
  // ── Booking Flow ──
  'booking.cart.title': { hy: 'Գրանցում {{n}} ծառայության համար', ru: 'Запись на {{n}} услуг(и) в Beauty Studio', en: 'Booking {{n}} service(s) at Beauty Studio' },
  'booking.cart.total': { hy: 'Ընդհանուր', ru: 'Итого', en: 'Total' },

  'step1.title': { hy: 'Ընտրեք ծառայություններ', ru: 'Выберите услуги', en: 'Select services' },
  'step1.cta': { hy: 'Ընտրել ժամը {{n}} ծառայության համար', ru: 'Выбрать время для {{n}} услуг(и)', en: 'Find a time for {{n}} service(s)' },

  'step2.title': { hy: 'Օր և ժամ', ru: 'День и время', en: 'Day and time' },
  'step2.morning': { hy: 'Առավոտ', ru: 'Утро', en: 'Morning' },
  'step2.afternoon': { hy: 'Կեսօրից հետո', ru: 'День', en: 'Afternoon' },
  'step2.no_times': { hy: 'Ազատ ժամեր չկան', ru: 'Нет свободного времени', en: 'No times available' },
  'step2.ends': { hy: 'ավարտվում է', ru: 'окончание в', en: 'ends' },
  'step2.checking': { hy: 'Ստուգում ենք ժամերը...', ru: 'Проверяем время...', en: 'Checking times...' },
  'step2.lock': { hy: 'Ամրագրել {{time}}-ը {{date}}-ին', ru: 'Забронировать {{time}} на {{date}}', en: 'Lock in {{time}} on {{date}}' },

  'step3.title': { hy: 'Ձեր տվյալները', ru: 'Ваши данные', en: 'Your details' },
  'step3.firstName': { hy: 'Անուն', ru: 'Имя', en: 'First name' },
  'step3.lastName': { hy: 'Ազգանուն', ru: 'Фамилия', en: 'Last name' },
  'step3.phone': { hy: 'Հեռախոս', ru: 'Мобильный телефон', en: 'Mobile phone' },
  'step3.email': { hy: 'Էլ. փոստ (ըստ ցանկության)', ru: 'Email (необязательно)', en: 'Email (optional)' },
  'step3.comments': { hy: 'Մեկնաբանություն (ըստ ցանկության)', ru: 'Комментарий (необязательно)', en: 'Comments (optional)' },
  'step3.remember': { hy: 'Հիշել ինձ', ru: 'Запомнить меня', en: 'Remember me' },
  'step3.policy': { hy: 'Չեղարկման կանոններ', ru: 'Политика отмены', en: 'Cancellation policy' },
  'step3.policyText': {
    hy: 'Այցից 24 ժամ առաջ հնարավոր չէ չեղարկել կամ փոփոխել:',
    ru: 'Отмена или изменение невозможны менее чем за 24 часа до визита.',
    en: 'No cancellations or changes allowed within 24 hours of the appointment.',
  },
  'step3.agree': { hy: 'Ես համաձայն եմ', ru: 'Я согласен(а)', en: 'I agree' },

  'booking.success': { hy: 'Հաստատված է!', ru: 'Запись подтверждена!', en: 'Booking Confirmed!' },
  'booking.success.desc': { hy: 'Ձեր գրանցումը հաջողությամբ ավարտվել է:', ru: 'Ваша запись успешно оформлена.', en: 'Your appointment has been scheduled successfully.' },
  'booking.another': { hy: 'Նոր գրանցում', ru: 'Записаться ещё', en: 'Book Another' },
  'booking.confirm': { hy: 'Հաստատել գրանցումը', ru: 'Подтвердить', en: 'Confirm Booking' },
  'booking.loading': { hy: 'Գրանցվում է...', ru: 'Записываем...', en: 'Booking...' },

  'loading': { hy: 'Բեռնվում է...', ru: 'Загрузка...', en: 'Loading...' },
  'loading.menu': { hy: 'Մենյուն բեռնվում է...', ru: 'Загрузка меню...', en: 'Fetching menu...' },
};

/**
 * Detect the user's language.
 * Priority: localStorage → Telegram language_code → default 'ru'
 */
export function detectLanguage() {
  const saved = localStorage.getItem('app_lang');
  if (saved && ['hy', 'ru', 'en'].includes(saved)) return saved;

  try {
    const tgLang = window.Telegram?.WebApp?.initDataUnsafe?.user?.language_code;
    if (tgLang) {
      if (tgLang.startsWith('hy')) return 'hy';
      if (tgLang.startsWith('ru')) return 'ru';
      if (tgLang.startsWith('en')) return 'en';
    }
  } catch {}

  return 'ru';
}

export function t(key, lang, params = {}) {
  const entry = translations[key];
  if (!entry) return key;
  let str = entry[lang] || entry['ru'] || key;
  
  if (params && typeof str === 'string') {
    for (const [k, v] of Object.entries(params)) {
      str = str.replace(new RegExp(`{{${k}}}`, 'g'), String(v));
    }
  }
  return str;
}
