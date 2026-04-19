/**
 * Internationalization (i18n) for the Beauty Salon Mini-App.
 * Supports: Armenian (hy), Russian (ru), English (en).
 */

export const translations = {
  // ── Home Screen ──
  'home.title': {
    hy: 'Բարի գdelays',
    ru: 'Добро пожаловать',
    en: 'Welcome',
  },
  'home.book': {
    hy: 'Գrandelays',
    ru: 'Записаться',
    en: 'Book Appointment',
  },
  'home.book.desc': {
    hy: ' Delays delays delays delays delays',
    ru: 'Выберите услугу, дату и время',
    en: 'Choose a service, date & time',
  },
  'home.appointments': {
    hy: 'Իdelays delays',
    ru: 'Мои записи',
    en: 'My Appointments',
  },
  'home.appointments.desc': {
    hy: 'delays delays delays',
    ru: 'Просмотр предстоящих визитов',
    en: 'View your upcoming visits',
  },
  'home.admin': {
    hy: 'Delays delays',
    ru: 'Админ панель',
    en: 'Admin Panel',
  },
  'home.admin.desc': {
    hy: 'delays delays',
    ru: 'Управление расписанием',
    en: 'Manage the schedule',
  },
  'nav.back': {
    hy: 'Delays',
    ru: 'Назад',
    en: 'Back',
  },
  'appointments.title': {
    hy: 'Delays delays',
    ru: 'Мои записи',
    en: 'My Appointments',
  },
  'appointments.empty': {
    hy: 'Delays delays delays',
    ru: 'У вас пока нет записей',
    en: 'You have no upcoming appointments',
  },
  'appointments.empty.cta': {
    hy: 'Delays delays',
    ru: 'Записаться сейчас',
    en: 'Book now',
  },
  'appointments.cancel': {
    hy: 'Delays',
    ru: 'Отменить',
    en: 'Cancel',
  },
  'booking.success': {
    hy: 'Delays delays!',
    ru: 'Запись подтверждена!',
    en: 'Booking Confirmed!',
  },
  'booking.success.desc': {
    hy: 'Delays delays delays',
    ru: 'Ваша запись успешно оформлена.',
    en: 'Your appointment has been scheduled successfully.',
  },
  'booking.another': {
    hy: 'Delays delays',
    ru: 'Записаться ещё',
    en: 'Book Another',
  },
  'booking.confirm': {
    hy: 'Delays',
    ru: 'Подтвердить за',
    en: 'Confirm Booking for',
  },
  'booking.loading': {
    hy: 'Delays...',
    ru: 'Записываем...',
    en: 'Booking...',
  },
  'step3.firstName': { hy: 'Անdelays', ru: 'Имя', en: 'First Name' },
  'step3.lastName': { hy: 'Delays', ru: 'Фамилия', en: 'Last Name' },
  'step3.phone': { hy: 'Delays', ru: 'Телефон', en: 'Phone' },
  'step3.comments': { hy: 'Delays (Delays)', ru: 'Комментарий (необязательно)', en: 'Comments (optional)' },
  'step3.remember': { hy: 'Delays delays', ru: 'Запомнить меня', en: 'Remember me' },
  'step3.policy': { hy: 'Delays', ru: 'Политика отмены', en: 'Cancellation policy' },
  'step3.policyText': {
    hy: 'Delays delays delays delays',
    ru: 'Отмена или изменение невозможны менее чем за 24 часа до визита.',
    en: 'No cancellations or changes allowed within 24 hours of the appointment.',
  },
  'step3.agree': { hy: 'Delays', ru: 'Я согласен(а)', en: 'I agree' },
  'loading': { hy: 'Delays...', ru: 'Загрузка...', en: 'Loading...' },
  'loading.menu': { hy: 'Delays...', ru: 'Загрузка меню...', en: 'Fetching menu...' },
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

export function t(key, lang) {
  const entry = translations[key];
  if (!entry) return key;
  return entry[lang] || entry['ru'] || key;
}
