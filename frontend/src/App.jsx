import React, { useState, useEffect, useMemo, useCallback } from 'react';
import { ChevronLeft, ChevronRight, ChevronDown, ChevronUp, ShoppingBag, Calendar, Clock, MapPin, Check, Info, User, Settings, X } from 'lucide-react';
import { t, detectLanguage } from './i18n';
import './index.css';

// Helper: Format duration from minutes
const formatDuration = (mins) => {
  if (!mins) return '';
  const h = Math.floor(mins / 60);
  const m = mins % 60;
  if (h > 0 && m > 0) return `${h}h ${m}m`;
  if (h > 0) return `${h}h`;
  return `${m}m`;
};

// Helper: Add minutes to HH:MM string -> Returns 24h format
const addMinutesToTime = (timeStr, minsToAdd) => {
  const [h, m] = timeStr.split(':').map(Number);
  const totalMins = h * 60 + m + minsToAdd;
  const newH = Math.floor(totalMins / 60);
  const newM = totalMins % 60;
  return `${String(newH).padStart(2, '0')}:${String(newM).padStart(2, '0')}`;
};

const formatTime24h = (timeStr) => {
  const [h, m] = timeStr.split(':').map(Number);
  return `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}`;
};

// ─── Global Summary Cart ─────────────────────────────────────
function SummaryCart({ selectedServices, selectedDate, selectedTime, lang }) {
  const totalPrice = selectedServices.reduce((acc, s) => acc + s.price, 0);
  const totalDuration = selectedServices.reduce((acc, s) => acc + s.duration, 0);

  const startStr = selectedTime ? formatTime24h(selectedTime) : null;
  const endStr = selectedTime ? addMinutesToTime(selectedTime, totalDuration) : null;

  let dateStr = null;
  if (selectedDate) {
    const d = new Date(selectedDate);
    dateStr = d.toLocaleDateString(lang === 'ru' ? 'ru-RU' : lang === 'hy' ? 'hy-AM' : 'en-US', { weekday: 'long', day: 'numeric', month: 'long' });
  }

  return (
    <div className="summary-wrapper fade-in">
      {/* Always show salon location */}
      <div className="summary-item">
        <MapPin className="summary-icon" size={16} />
        <div className="summary-details">
          <div className="summary-line" style={{ fontWeight: '500' }}>Beauty Studio</div>
          <div className="summary-subline">14 Tumanyan St, Yerevan, Armenia</div>
        </div>
      </div>

      {selectedServices.length > 0 && (
        <div className="summary-item" style={{ marginTop: '4px' }}>
          <ShoppingBag className="summary-icon" size={16} />
          <div className="summary-details">
            {selectedServices.map(s => (
              <div key={s.service_id} style={{ marginBottom: '4px' }}>
                <div className="summary-line">
                  <span style={{ paddingRight: '8px' }}>{s.name}</span>
                  <span style={{ whiteSpace: 'nowrap' }}>{s.price} ֏</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {selectedDate && (
        <div className="summary-item">
          <Calendar className="summary-icon" size={16} />
          <div className="summary-details">
            <div className="summary-line" style={{ fontWeight: '500' }}>{dateStr}</div>
          </div>
        </div>
      )}

      {selectedTime && (
        <div className="summary-item">
          <Clock className="summary-icon" size={16} />
          <div className="summary-details">
            <div className="summary-line" style={{ fontWeight: '500' }}>{startStr} – {endStr} ({formatDuration(totalDuration)})</div>
          </div>
        </div>
      )}

      {totalPrice > 0 && (
        <div style={{ borderTop: '1px solid var(--border-color)', marginTop: 'var(--spacing-sm)', paddingTop: 'var(--spacing-sm)', display: 'flex', justifyContent: 'space-between', fontWeight: '600', fontSize: '14px' }}>
          <span>{t('booking.cart.total', lang)}</span>
          <span>{totalPrice} ֏</span>
        </div>
      )}
    </div>
  );
}

// ─── Loading Component ───────────────────────────────────────
function LoadingSpinner({ text = "Loading..." }) {
  return (
    <div className="loading-wrap">
      <div className="spinner" />
      <div>{text}</div>
    </div>
  );
}

// ─── Main App ────────────────────────────────────────────────
export default function App() {
  const [page, setPage] = useState('home'); // 'home' | 'booking' | 'appointments'
  const [lang, setLang] = useState(() => detectLanguage());
  const [step, setStep] = useState(1);
  const [isCartOpen, setIsCartOpen] = useState(false);

  // Data from API
  const [categories, setCategories] = useState([]);
  const [services, setServices] = useState([]);
  const [dataLoading, setDataLoading] = useState(true);

  // Admin detection
  const [adminId, setAdminId] = useState(null);
  const tgUser = window.Telegram?.WebApp?.initDataUnsafe?.user;
  const isAdmin = adminId && tgUser && tgUser.id === adminId;

  // Selections
  const [selectedServices, setSelectedServices] = useState([]);
  const [selectedDate, setSelectedDate] = useState(null);
  const [selectedTime, setSelectedTime] = useState(null);

  // Form Details
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [phone, setPhone] = useState('');
  const [countryCode, setCountryCode] = useState('+374');
  const [email, setEmail] = useState('');
  const [comments, setComments] = useState('');
  const [rememberMe, setRememberMe] = useState(false);
  const [policyAgreed, setPolicyAgreed] = useState(false);

  const [bookingLoading, setBookingLoading] = useState(false);
  const [bookingSuccess, setBookingSuccess] = useState(false);

  // Appointments
  const [appointments, setAppointments] = useState([]);
  const [appointmentsLoading, setAppointmentsLoading] = useState(false);

  // Language switcher
  const changeLang = (newLang) => {
    setLang(newLang);
    localStorage.setItem('app_lang', newLang);
  };

  // Initialize data
  useEffect(() => {
    try { window.Telegram.WebApp.ready(); window.Telegram.WebApp.expand(); } catch {}
    
    async function loadData() {
      try {
        const [catRes, svcRes, cfgRes] = await Promise.all([
          fetch('/api/categories'),
          fetch('/api/services'),
          fetch('/api/config'),
        ]);
        setCategories(await catRes.json());
        setServices(await svcRes.json());
        const cfg = await cfgRes.json();
        setAdminId(cfg.admin_id);
      } catch (err) {
        console.error('Failed to load data:', err);
      } finally {
        setDataLoading(false);
      }
    }
    loadData();
  }, []);

  // Load appointments when navigating to that page
  const loadAppointments = useCallback(async () => {
    if (!tgUser?.id) return;
    setAppointmentsLoading(true);
    try {
      const res = await fetch(`/api/appointments?user_id=${tgUser.id}`);
      const data = await res.json();
      // Enrich with service names
      for (const apt of data) {
        let sids = apt.service_ids;
        if (typeof sids === 'string') sids = JSON.parse(sids);
        const names = services.filter(s => sids.includes(s.service_id)).map(s => s.name);
        apt._serviceNames = names;
        apt._totalPrice = services.filter(s => sids.includes(s.service_id)).reduce((a, s) => a + s.price, 0);
      }
      setAppointments(data);
    } catch (err) {
      console.error('Failed to load appointments:', err);
    } finally {
      setAppointmentsLoading(false);
    }
  }, [tgUser?.id, services]);

  const goToBooking = () => {
    setStep(1);
    setSelectedServices([]);
    setSelectedDate(null);
    setSelectedTime(null);
    setBookingSuccess(false);
    setPage('booking');
  };

  const goToAppointments = () => {
    setPage('appointments');
    loadAppointments();
  };

  const goHome = () => {
    setPage('home');
    setBookingSuccess(false);
  };

  if (dataLoading) {
    return <LoadingSpinner text={t('loading.menu', lang)} />;
  }

  // ── HOME SCREEN ──
  if (page === 'home') {
    return (
      <div className="app-container">
        <div className="home-screen fade-in">
          {/* Language Toggle */}
          <div className="lang-toggle">
            {['hy', 'ru', 'en'].map(code => (
              <button
                key={code}
                className={`lang-btn ${lang === code ? 'active' : ''}`}
                onClick={() => changeLang(code)}
              >
                {code === 'hy' ? '🇦🇲' : code === 'ru' ? '🇷🇺' : '🇬🇧'}
              </button>
            ))}
          </div>

          {/* Hero */}
          <div className="home-hero">
            <div className="home-logo">💅</div>
            <h1 className="home-title">{t('home.title', lang)}</h1>
            <p className="home-subtitle">Beauty Studio</p>
          </div>

          {/* Navigation Cards */}
          <div className="home-cards">
            <button className="menu-card" onClick={goToBooking}>
              <div className="menu-card-icon" style={{ background: 'linear-gradient(135deg, #007aff, #00c6ff)' }}>
                <Calendar size={28} color="#fff" />
              </div>
              <div className="menu-card-text">
                <div className="menu-card-title">{t('home.book', lang)}</div>
                <div className="menu-card-desc">{t('home.book.desc', lang)}</div>
              </div>
              <ChevronRight size={20} className="menu-card-arrow" />
            </button>

            <button className="menu-card" onClick={goToAppointments}>
              <div className="menu-card-icon" style={{ background: 'linear-gradient(135deg, #10b981, #34d399)' }}>
                <User size={28} color="#fff" />
              </div>
              <div className="menu-card-text">
                <div className="menu-card-title">{t('home.appointments', lang)}</div>
                <div className="menu-card-desc">{t('home.appointments.desc', lang)}</div>
              </div>
              <ChevronRight size={20} className="menu-card-arrow" />
            </button>

            {isAdmin && (
              <button className="menu-card" onClick={() => {
                // Open a deep-link to the bot's /admin command
                try {
                  window.Telegram.WebApp.openTelegramLink('https://t.me/tpodologbot?start=admin');
                } catch {
                  alert('Send /admin to the bot');
                }
              }}>
                <div className="menu-card-icon" style={{ background: 'linear-gradient(135deg, #f59e0b, #f97316)' }}>
                  <Settings size={28} color="#fff" />
                </div>
                <div className="menu-card-text">
                  <div className="menu-card-title">{t('home.admin', lang)}</div>
                  <div className="menu-card-desc">{t('home.admin.desc', lang)}</div>
                </div>
                <ChevronRight size={20} className="menu-card-arrow" />
              </button>
            )}
          </div>

          {/* Address Footer */}
          <div className="home-footer">
            <MapPin size={14} />
            <span>14 Tumanyan St, Yerevan</span>
          </div>
        </div>
      </div>
    );
  }

  // ── MY APPOINTMENTS SCREEN ──
  if (page === 'appointments') {
    return (
      <div className="app-container">
        <div className="nav-header fade-in">
          <button className="back-button" onClick={goHome}>
            <ChevronLeft size={20} />
          </button>
          <h1 style={{ marginBottom: 0 }}>{t('appointments.title', lang)}</h1>
        </div>

        <div className="appointments-list fade-in">
          {appointmentsLoading ? (
            <LoadingSpinner text={t('loading', lang)} />
          ) : appointments.length === 0 ? (
            <div className="empty-state">
              <Calendar size={48} className="empty-icon" />
              <p>{t('appointments.empty', lang)}</p>
              <button className="btn-primary" onClick={goToBooking}>
                {t('appointments.empty.cta', lang)}
              </button>
            </div>
          ) : (
            appointments.map(apt => {
              const dateObj = new Date(apt.appointment_date);
              const dateLabel = dateObj.toLocaleDateString(lang === 'ru' ? 'ru-RU' : lang === 'hy' ? 'hy-AM' : 'en-US', {
                weekday: 'short', day: 'numeric', month: 'long'
              });
              const endTime = addMinutesToTime(apt.appointment_time, apt.total_duration);

              return (
                <div key={apt.appointment_id} className="appointment-card">
                  <div className="apt-date-badge">
                    <div className="apt-day">{dateObj.getDate()}</div>
                    <div className="apt-month">{dateObj.toLocaleDateString(lang === 'ru' ? 'ru-RU' : 'en-US', { month: 'short' })}</div>
                  </div>
                  <div className="apt-details">
                    <div className="apt-time">
                      <Clock size={14} />
                      {apt.appointment_time} – {endTime} ({formatDuration(apt.total_duration)})
                    </div>
                    <div className="apt-services">
                      {(apt._serviceNames || []).join(', ')}
                    </div>
                    {apt._totalPrice > 0 && (
                      <div className="apt-price">{apt._totalPrice} ֏</div>
                    )}
                  </div>
                  <button
                    className="apt-cancel-btn"
                    onClick={async () => {
                      if (!confirm(t('appointments.cancel', lang) + '?')) return;
                      try {
                        await fetch(`/api/bookings/${apt.appointment_id}/cancel`, { method: 'PATCH' });
                        loadAppointments();
                      } catch {}
                    }}
                  >
                    <X size={16} />
                  </button>
                </div>
              );
            })
          )}
        </div>
      </div>
    );
  }

  // ── BOOKING FLOW ──
  if (bookingSuccess) {
    return (
      <div className="app-container" style={{ justifyContent: 'center', alignItems: 'center', padding: '40px' }}>
        <div style={{ background: '#10b981', color: '#fff', padding: '20px', borderRadius: '50%', marginBottom: '24px' }}>
          <Check size={48} />
        </div>
        <h1 style={{ marginBottom: '16px' }}>{t('booking.success', lang)}</h1>
        <p className="text-hint" style={{ textAlign: 'center', marginBottom: '32px' }}>
          {t('booking.success.desc', lang)}
        </p>
        <button className="btn-primary" onClick={goHome}>
          {t('booking.another', lang)}
        </button>
      </div>
    );
  }

  return (
    <div className="app-container">
      <div className="main-content">
        {/* Left Panel: Active Step */}
        <div className="left-panel">

          {step === 1 && (
            <Step1Services 
              categories={categories} 
              services={services} 
              selectedServices={selectedServices}
              setSelectedServices={setSelectedServices}
              onBack={goHome}
              onNext={() => setStep(2)}
              lang={lang}
            />
          )}
          {step === 2 && (
            <Step2DateTime
              selectedServices={selectedServices}
              selectedDate={selectedDate}
              setSelectedDate={setSelectedDate}
              selectedTime={selectedTime}
              setSelectedTime={setSelectedTime}
              onNext={() => setStep(3)}
              onBack={() => setStep(1)}
              lang={lang}
            />
          )}
          {step === 3 && (
            <Step3Details
              selectedServices={selectedServices}
              firstName={firstName} setFirstName={setFirstName}
              lastName={lastName} setLastName={setLastName}
              phone={phone} setPhone={setPhone}
              countryCode={countryCode} setCountryCode={setCountryCode}
              email={email} setEmail={setEmail}
              comments={comments} setComments={setComments}
              rememberMe={rememberMe} setRememberMe={setRememberMe}
              policyAgreed={policyAgreed} setPolicyAgreed={setPolicyAgreed}
              onBook={async () => {
                setBookingLoading(true);
                try {
                  const payload = {
                    service_ids: selectedServices.map(s => s.service_id),
                    date: selectedDate,
                    time: selectedTime,
                    name: `${firstName} ${lastName}`.trim(),
                    phone: `${countryCode} ${phone}`.trim(),
                    comments,
                    telegram_user_id: tgUser?.id || null
                  };
                  const res = await fetch('/api/bookings', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                  });
                  if (res.ok) {
                    setBookingSuccess(true);
                  } else {
                    alert('Booking failed. The time slot may no longer be available.');
                  }
                } catch (e) {
                  alert('Network error while booking.');
                }
                setBookingLoading(false);
              }}
              bookingLoading={bookingLoading}
              onBack={() => setStep(2)}
              lang={lang}
            />
          )}
        </div>

        {/* Right Panel: Summary Cart */}
        <div className="right-panel">
          <div className="mobile-cart-toggle" onClick={() => setIsCartOpen(!isCartOpen)}>
            <span>
              {t('booking.cart.title', lang, { n: selectedServices.length })}
            </span>
            <ChevronDown size={16} style={{ transform: isCartOpen ? 'rotate(180deg)' : 'rotate(0)' }} className="cart-chevron" />
          </div>
          
          <div className={`cart-collapse ${isCartOpen ? 'open' : ''}`}>
            <div className="cart-content">
              <div className="cart-inner">
                <SummaryCart 
                  selectedServices={selectedServices}
                  selectedDate={selectedDate}
                  selectedTime={selectedTime}
                  lang={lang}
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

// ─── STEP 1: Services ─────────────────────────────────────────
function Step1Services({ categories, services, selectedServices, setSelectedServices, onBack, onNext, lang }) {
  const [expandedCat, setExpandedCat] = useState(categories[0]?.category_id);

  const toggleService = (svc) => {
    const isSelected = selectedServices.some(s => s.service_id === svc.service_id);
    if (isSelected) {
      setSelectedServices(selectedServices.filter(s => s.service_id !== svc.service_id));
    } else {
      setSelectedServices([...selectedServices, svc]);
    }
  };

  return (
    <div className="fade-in" style={{ display: 'flex', flexDirection: 'column' }}>
      <div className="nav-header">
        <button className="back-button" onClick={onBack}>
          <ChevronLeft size={20} />
        </button>
        <h1 style={{ marginBottom: 0 }}>{t('step1.title', lang)}</h1>
      </div>

      <div style={{ flex: 1 }}>
        {categories.map(cat => {
          const catServices = services.filter(s => s.category_id === cat.category_id);
          const selectedInCat = catServices.filter(s => selectedServices.some(sel => sel.service_id === s.service_id)).length;
          const isExpanded = expandedCat === cat.category_id;

          return (
            <div key={cat.category_id} className="accordion">
              <button 
                className="accordion-header"
                onClick={() => setExpandedCat(isExpanded ? null : cat.category_id)}
              >
                <div style={{ display: 'flex', alignItems: 'center' }}>
                  {cat.name}
                  {selectedInCat > 0 && <span className="badge">{selectedInCat}</span>}
                </div>
                <ChevronDown size={20} style={{ transform: isExpanded ? 'rotate(180deg)' : 'rotate(0)' }} />
              </button>
              
              <div className={`accordion-collapse ${isExpanded ? 'expanded' : ''}`}>
                <div className="accordion-content">
                  <div className="accordion-inner">
                    {catServices.map(svc => {
                      const isChecked = selectedServices.some(s => s.service_id === svc.service_id);
                      return (
                        <div key={svc.service_id} className="service-item" onClick={() => toggleService(svc)}>
                          <div className={`checkbox ${isChecked ? 'checked' : ''}`}>
                            {isChecked && <Check size={14} />}
                          </div>
                          <div className="service-details">
                            <div className="service-title">{svc.name}</div>
                            <div className="service-meta">
                              {formatDuration(svc.duration)} · {svc.price} ֏
                            </div>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {selectedServices.length > 0 && (
        <div className="sticky-bottom">
          <button 
            className="btn-primary" 
            onClick={onNext}
            style={{ marginTop: 0 }}
          >
            {t('step1.cta', lang, { n: selectedServices.length })}
          </button>
        </div>
      )}
    </div>
  );
}

// ─── STEP 2: Date & Time ──────────────────────────────────────
function Step2DateTime({ selectedServices, selectedDate, setSelectedDate, selectedTime, setSelectedTime, onNext, onBack, lang }) {
  const [currentMonthDate, setCurrentMonthDate] = useState(new Date());
  const [monthAvail, setMonthAvail] = useState({});
  const [slotsLoading, setSlotsLoading] = useState(false);
  const [slots, setSlots] = useState([]);

  const service_ids = useMemo(() => selectedServices.map(s => s.service_id).join(','), [selectedServices]);
  const totalDuration = useMemo(() => selectedServices.reduce((acc, s) => acc + s.duration, 0), [selectedServices]);

  // Load Month Availability Dots
  useEffect(() => {
    const year = currentMonthDate.getFullYear();
    const month = currentMonthDate.getMonth() + 1;
    fetch(`/api/slots/month?year=${year}&month=${month}&service_ids=${service_ids}`)
      .then(r => r.json())
      .then(data => setMonthAvail(data))
      .catch(() => {});
  }, [currentMonthDate, service_ids]);

  // Load Daily Slots
  useEffect(() => {
    if (!selectedDate) return;
    setSlotsLoading(true);
    setSelectedTime(null);
    fetch(`/api/slots?date=${selectedDate}&service_ids=${service_ids}`)
      .then(r => r.json())
      .then(data => setSlots(data))
      .catch(() => setSlots([]))
      .finally(() => setSlotsLoading(false));
  }, [selectedDate, service_ids, setSelectedTime]);

  // Render Calendar Grid
  const renderCalendar = () => {
    const year = currentMonthDate.getFullYear();
    const month = currentMonthDate.getMonth();
    const daysInMonth = new Date(year, month + 1, 0).getDate();
    const firstDayIndex = new Date(year, month, 1).getDay(); // 0 is Sunday
    
    const days = [];
    for (let i = 0; i < firstDayIndex; i++) {
      days.push(<div key={`empty-${i}`} className="calendar-day disabled"></div>);
    }
    
    const today = new Date();
    today.setHours(0, 0, 0, 0);

    for (let d = 1; d <= daysInMonth; d++) {
      const dateStr = `${year}-${String(month + 1).padStart(2, '0')}-${String(d).padStart(2, '0')}`;
      const cellDate = new Date(year, month, d);
      const isPast = cellDate < today;
      const isSelected = selectedDate === dateStr;
      const avail = monthAvail[dateStr];
      const hasAvailData = !!avail;
      const hasAnyAvail = hasAvailData ? (avail.morning || avail.afternoon) : true; // assume available until data loads

      const isDisabled = isPast || (hasAvailData && !hasAnyAvail);

      days.push(
        <div 
          key={dateStr}
          className={`calendar-day ${isSelected ? 'active' : ''} ${isDisabled ? 'disabled' : ''}`}
          onClick={() => {
            if (!isDisabled) setSelectedDate(dateStr);
          }}
        >
          {d}
          {(!isPast && !isSelected && hasAvailData) && (
            <div className="day-dots">
              <div className={`dot ${!avail.morning ? 'disabled' : ''}`} />
              <div className={`dot ${!avail.afternoon ? 'disabled' : ''}`} style={avail.afternoon ? { background: '#3b82f6' } : {}} />
            </div>
          )}
        </div>
      );
    }

    return (
      <div style={{ marginBottom: '24px', boxShadow: '0 2px 10px rgba(0,0,0,0.02)' }}>
        <div className="calendar-header">
          <div style={{ fontWeight: '600', fontSize: '15px' }}>
            {currentMonthDate.toLocaleString('default', { month: 'long', year: 'numeric' })}
          </div>
          <div style={{ display: 'flex', gap: '8px' }}>
            <button 
              className="calendar-nav" 
              onClick={() => setCurrentMonthDate(new Date(year, month - 1, 1))}
            >
              <ChevronLeft size={20} />
            </button>
            <button 
              className="calendar-nav" 
              onClick={() => setCurrentMonthDate(new Date(year, month + 1, 1))}
            >
              <ChevronRight size={20} />
            </button>
          </div>
        </div>
        <div className="calendar-grid">
          {['S', 'M', 'T', 'W', 'T', 'F', 'S'].map((day, i) => (
            <div key={i} className="calendar-day-header">{day}</div>
          ))}
          {days}
        </div>
      </div>
    );
  };

  const morningSlots = slots.filter(s => parseInt(s.time.split(':')[0], 10) < 12);
  const afternoonSlots = slots.filter(s => parseInt(s.time.split(':')[0], 10) >= 12);

  return (
    <div className="fade-in" style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      <div className="nav-header">
        <button className="back-button" onClick={onBack}>
          <ChevronLeft size={20} />
        </button>
        <h1 style={{ marginBottom: 0 }}>{t('step2.title', lang)}</h1>
      </div>

      {renderCalendar()}

      {selectedDate && (
        <div style={{ flex: 1 }}>
          {slotsLoading ? (
            <LoadingSpinner text={t('step2.checking', lang)} />
          ) : (
            <div className="time-cols">
              <div>
                <div className="time-header">{t('step2.morning', lang)}</div>
                {morningSlots.length === 0 ? <p className="text-hint">{t('step2.no_times', lang)}</p> : (
                  <div className="slot-list">
                    {morningSlots.map((s, i) => renderTimeSlot(s, i))}
                  </div>
                )}
              </div>
              <div>
                <div className="time-header">{t('step2.afternoon', lang)}</div>
                {afternoonSlots.length === 0 ? <p className="text-hint">{t('step2.no_times', lang)}</p> : (
                  <div className="slot-list">
                    {afternoonSlots.map((s, i) => renderTimeSlot(s, i))}
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      )}

      {selectedTime && (
        <div className="sticky-bottom">
          <button 
            className="btn-primary" 
            onClick={onNext}
            style={{ marginTop: 0 }}
          >
            {t('step2.lock', lang, { time: formatTime24h(selectedTime), date: new Date(selectedDate).toLocaleDateString(lang === 'ru' ? 'ru-RU' : lang === 'hy' ? 'hy-AM' : 'en-US', { month: 'short', day: 'numeric' }) })}
          </button>
        </div>
      )}
    </div>
  );

  function renderTimeSlot(s, index) {
    const isSelected = selectedTime === s.time;
    let cn = `time-slot ${isSelected ? 'active' : ''} ${!s.available ? 'disabled' : ''}`;
    
    return (
      <button 
        key={s.time}
        className={cn}
        disabled={!s.available}
        onClick={() => s.available && setSelectedTime(s.time)}
        style={{ animationDelay: `${index * 0.035}s` }}
      >
        <span style={{ fontWeight: '500', fontSize: '15px' }}>{formatTime24h(s.time)}</span>
        {isSelected && (
          <span className="slot-ends">{t('step2.ends', lang)} {addMinutesToTime(s.time, totalDuration)}</span>
        )}
      </button>
    );
  }
}

// ─── STEP 3: Details ──────────────────────────────────────────
function Step3Details({
  selectedServices,
  firstName, setFirstName, lastName, setLastName,
  phone, setPhone, countryCode, setCountryCode, email, setEmail,
  comments, setComments,
  rememberMe, setRememberMe,
  policyAgreed, setPolicyAgreed,
  onBook, bookingLoading, onBack, lang
}) {
  const [showTooltip, setShowTooltip] = useState(false);
  const isValid = firstName.trim() && lastName.trim() && phone.trim() && policyAgreed;
  const totalPrice = selectedServices.reduce((acc, s) => acc + s.price, 0);

  return (
    <div className="fade-in" style={{ display: 'flex', flexDirection: 'column' }}>
      <div className="nav-header">
        <button className="back-button" onClick={onBack}>
          <ChevronLeft size={20} />
        </button>
        <h1 style={{ marginBottom: 0 }}>{t('step3.title', lang)}</h1>
      </div>

      <div style={{ flex: 1 }}>
        <div className="form-group">
          <label className="form-label">{t('step3.firstName', lang)}</label>
          <input className="form-input" value={firstName} onChange={e => setFirstName(e.target.value)} />
        </div>
        <div className="form-group">
          <label className="form-label">{t('step3.lastName', lang)}</label>
          <input className="form-input" value={lastName} onChange={e => setLastName(e.target.value)} />
        </div>

        <div className="form-group">
          <label className="form-label">{t('step3.email', lang)}</label>
          <input type="email" className="form-input" value={email} onChange={e => setEmail(e.target.value)} />
        </div>

        <div className="form-group">
          <label className="form-label">{t('step3.phone', lang)}</label>
          <div className="phone-input-wrapper">
            <div className="phone-prefix">
              <select 
                className="country-select"
                value={countryCode}
                onChange={e => setCountryCode(e.target.value)}
              >
                <option value="+374">🇦🇲 +374</option>
                <option value="+7">🇷🇺 +7</option>
                <option value="+995">🇬🇪 +995</option>
                <option value="+1">🇺🇸 +1</option>
                <option value="+33">🇫🇷 +33</option>
                <option value="+49">🇩🇪 +49</option>
                <option value="+971">🇦🇪 +971</option>
                <option value="+44">🇬🇧 +44</option>
                <option value="+380">🇺🇦 +380</option>
                <option value="+375">🇧🇾 +375</option>
              </select>
            </div>
            <input 
              type="tel" 
              className="form-input phone-input-field" 
              value={phone} 
              onChange={e => {
                const val = e.target.value.replace(/[^\d\s-]/g, '');
                setPhone(val);
              }} 
              placeholder="99 123456" 
            />
          </div>
        </div>

        <div className="form-group">
          <label className="form-label">{t('step3.comments', lang)}</label>
          <textarea 
            className="form-input" 
            maxLength={250} 
            value={comments} 
            onChange={e => setComments(e.target.value)} 
          />
          <div className="text-hint" style={{ textAlign: 'right', marginTop: '4px', fontSize: '11px' }}>
            {250 - comments.length}
          </div>
        </div>

        {/* Remember me */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '24px', position: 'relative' }}>
          <div 
            className={`checkbox ${rememberMe ? 'checked' : ''}`} 
            onClick={() => setRememberMe(!rememberMe)}
            style={{ cursor: 'pointer' }}
          >
            {rememberMe && <Check size={14} />}
          </div>
          <span style={{ fontSize: '14px' }}>{t('step3.remember', lang)}</span>
          <Info 
            size={16} 
            color="var(--text-secondary)" 
            style={{ cursor: 'pointer' }} 
            onMouseEnter={() => setShowTooltip(true)}
            onMouseLeave={() => setShowTooltip(false)}
          />
          {showTooltip && (
            <div style={{
              position: 'absolute', top: '100%', left: '0', zIndex: 100, 
              background: 'var(--primary-color)', color: '#fff', 
              padding: '12px', borderRadius: '8px', fontSize: '13px', width: '300px',
              boxShadow: '0 4px 6px rgba(0,0,0,0.1)', marginTop: '8px'
            }}>
              <strong>Remember your details</strong><br/>
              Ticking this box will store your details on this computer and automatically complete them for future bookings. If you are using a shared or public computer you should not tick this box.
            </div>
          )}
        </div>

        {/* Cancellation Policy */}
        <div className="policy-box">
          <div style={{ fontWeight: '600', marginBottom: '4px', fontSize: '14px' }}>{t('step3.policy', lang)}</div>
          <div className="text-hint" style={{ marginBottom: '12px' }}>
            {t('step3.policyText', lang)}
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer' }} onClick={() => setPolicyAgreed(!policyAgreed)}>
            <div className={`checkbox ${policyAgreed ? 'checked' : ''}`}>
              {policyAgreed && <Check size={14} />}
            </div>
            <span style={{ fontSize: '14px', fontWeight: '500' }}>{t('step3.agree', lang)}</span>
          </div>
        </div>
      </div>

      <div className="sticky-bottom">
        <button 
          className={`btn-primary ${bookingLoading ? 'loading' : ''}`} 
          onClick={onBook}
          disabled={!isValid || bookingLoading}
          style={{ marginTop: 0 }}
        >
          {bookingLoading ? t('booking.loading', lang) : `${t('booking.confirm', lang)} ${totalPrice} ֏`}
        </button>
      </div>
    </div>
  );
}
