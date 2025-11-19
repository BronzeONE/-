const API_BASE = 'http://localhost:8000/api';
const state = {
  token: null,
  user: null,
  profile: null,
  orders: [],
  purchases: [],
};

const registrationSection = document.getElementById('registration-section');
const loginSection = document.getElementById('login-section');
const authStatusEl = document.getElementById('auth-status');
const profileSection = document.getElementById('profile-section');
const profileForm = document.getElementById('profile-form');
const navAuthGroup = document.getElementById('nav-auth-group');
const navShowLogin = document.getElementById('nav-show-login');
const navShowRegister = document.getElementById('nav-show-register');
const navProfileBtn = document.getElementById('nav-profile');
const participationBtn = document.getElementById('participation-toggle');
const profileStatus = document.getElementById('profile-status');
const ordersSection = document.getElementById('orders-section');
const ordersList = document.getElementById('orders-list');
const purchasesSection = document.getElementById('purchases-section');
const purchasesList = document.getElementById('purchases-list');
const toastEl = document.getElementById('toast');
const registrationForm = document.getElementById('registration-form');
const loginForm = document.getElementById('login-form');

let currentAuthView = 'register';

function showToast(message, timeout = 3000) {
  toastEl.textContent = message;
  toastEl.classList.remove('hidden');
  setTimeout(() => toastEl.classList.add('hidden'), timeout);
}

function showAuthForm(mode) {
  currentAuthView = mode === 'login' ? 'login' : 'register';

  if (currentAuthView === 'login') {
    registrationSection?.classList.add('hidden');
    loginSection?.classList.remove('hidden');
    navShowLogin?.classList.add('active');
    navShowRegister?.classList.remove('active');
  } else {
    registrationSection?.classList.remove('hidden');
    loginSection?.classList.add('hidden');
    navShowRegister?.classList.add('active');
    navShowLogin?.classList.remove('active');
  }
}

function setAuthState({ token, user }) {
  state.token = token;
  state.user = user;
  if (token) {
    if (authStatusEl) {
      authStatusEl.textContent = `Авторизован: ${user.phone_number}`;
    }
    navAuthGroup?.classList.add('hidden');
    registrationSection?.classList.add('hidden');
    loginSection?.classList.add('hidden');
    profileSection?.classList.remove('hidden');
    ordersSection?.classList.remove('hidden');
    purchasesSection?.classList.remove('hidden');
    if (navProfileBtn) {
      navProfileBtn.classList.remove('hidden');
    }
    loadInitialData().catch((error) => console.error(error));
  } else {
    if (authStatusEl) {
      authStatusEl.textContent = 'Не авторизован';
    }
    navAuthGroup?.classList.remove('hidden');
    showAuthForm(currentAuthView);
    profileSection?.classList.add('hidden');
    ordersSection?.classList.add('hidden');
    purchasesSection?.classList.add('hidden');
    if (navProfileBtn) {
      navProfileBtn.classList.add('hidden');
    }
  }
}

async function apiRequest(url, options = {}) {
  const headers = options.headers || {};
  if (state.token) {
    headers.Authorization = `Token ${state.token}`;
  }

  const response = await fetch(`${API_BASE}${url}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...headers,
    },
  });

  if (!response.ok) {
    const errorBody = await response.json().catch(() => ({}));
    
    // Если есть детали ошибки валидации, возвращаем их
    if (errorBody.detail) {
      throw new Error(errorBody.detail);
    }
    
    // Если есть ошибки полей (валидация), возвращаем их
    if (errorBody && typeof errorBody === 'object' && Object.keys(errorBody).length > 0) {
      throw new Error(JSON.stringify(errorBody));
    }
    
    throw new Error(`Ошибка ${response.status}: ${response.statusText}`);
  }

  if (response.status === 204) {
    return null;
  }
  return response.json();
}

async function loadInitialData() {
  await Promise.all([loadProfile(), loadOrders(), loadPurchases()]).catch((error) => {
    console.error(error);
    showToast(`Ошибка загрузки данных: ${error.message}`);
  });
}

async function loadProfile() {
  const profile = await apiRequest('/profile/me/');
  state.profile = profile;
  fillProfileForm(profile);
}

registrationForm?.addEventListener('submit', async (event) => {
  event.preventDefault();
  const formData = new FormData(registrationForm);
  const payload = Object.fromEntries(formData.entries());

  try {
    const data = await apiRequest('/auth/register/', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
    showToast('Регистрация успешна!');
    registrationForm.reset();
    setAuthState(data);
  } catch (error) {
    console.error(error);
    showToast(`Ошибка регистрации: ${error.message}`);
  }
});

loginForm?.addEventListener('submit', async (event) => {
  event.preventDefault();
  const formData = new FormData(loginForm);
  const payload = Object.fromEntries(formData.entries());

  try {
    const data = await apiRequest('/auth/login/', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
    showToast('Вход выполнен.');
    loginForm.reset();
    setAuthState(data);
  } catch (error) {
    console.error(error);
    showToast(`Ошибка входа: ${error.message}`);
  }
});

// Multi-step form management
let currentStep = 1;
const totalSteps = 6;
const stepTitles = {
  1: 'Базовая информация',
  2: 'Контент и платформа',
  3: 'Аудитория',
  4: 'Опыт и сотрудничество',
  5: 'Формат сотрудничества',
  6: 'Дополнительно'
};

function updateStepDisplay() {
  const currentStepEl = document.getElementById('current-step');
  const stepTitleEl = document.getElementById('step-title');
  const prevBtn = document.getElementById('prev-step-btn');
  const nextBtn = document.getElementById('next-step-btn');
  const submitBtn = document.getElementById('submit-btn');
  
  if (currentStepEl) currentStepEl.textContent = currentStep;
  if (stepTitleEl) stepTitleEl.textContent = stepTitles[currentStep] || '';
  
  // Show/hide navigation buttons
  if (prevBtn) {
    if (currentStep === 1) {
      prevBtn.classList.add('hidden');
    } else {
      prevBtn.classList.remove('hidden');
    }
  }
  
  if (nextBtn && submitBtn) {
    if (currentStep === totalSteps) {
      nextBtn.classList.add('hidden');
      submitBtn.classList.remove('hidden');
    } else {
      nextBtn.classList.remove('hidden');
      submitBtn.classList.add('hidden');
    }
  }
  
  // Show/hide form steps and manage required attributes
  document.querySelectorAll('.form-step').forEach((step, index) => {
    const stepNum = index + 1;
    if (stepNum === currentStep) {
      step.classList.remove('hidden');
      // Восстанавливаем required для видимого шага
      step.querySelectorAll('[data-required]').forEach(field => {
        field.setAttribute('required', '');
      });
    } else {
      step.classList.add('hidden');
      // Убираем required с полей на скрытых шагах
      step.querySelectorAll('[required]').forEach(field => {
        field.setAttribute('data-required', '');
        field.removeAttribute('required');
      });
    }
  });
}

function goToStep(step) {
  if (step < 1 || step > totalSteps) return;
  
  const currentStepEl = document.querySelector(`.form-step[data-step="${currentStep}"]`);
  if (currentStepEl) {
    let isValid = true;
    
    if (step > currentStep) {
      // Проверяем только видимые поля (не скрытые)
      const isVisible = (element) => {
        if (!element) return false;
        const style = window.getComputedStyle(element);
        return style.display !== 'none' && style.visibility !== 'hidden' && style.opacity !== '0';
      };
      
      // Проверка текстовых полей, textarea и select (только видимые)
      const requiredInputs = currentStepEl.querySelectorAll('input[required]:not([type="radio"]):not([type="checkbox"]), textarea[required], select[required]');
      requiredInputs.forEach(field => {
        if (!isVisible(field)) return; // Пропускаем скрытые поля
        
        const value = field.value ? field.value.trim() : '';
        if (!value) {
          isValid = false;
          field.style.borderColor = '#f04444';
        } else {
          field.style.borderColor = '';
        }
      });
      
      // Проверка радио-кнопок (должна быть выбрана хотя бы одна в группе, только видимые)
      const radioGroups = {};
      currentStepEl.querySelectorAll('input[type="radio"][required]').forEach(radio => {
        if (!isVisible(radio)) return; // Пропускаем скрытые поля
        
        const name = radio.name;
        if (!radioGroups[name]) {
          radioGroups[name] = [];
        }
        radioGroups[name].push(radio);
      });
      
      Object.keys(radioGroups).forEach(name => {
        const checked = currentStepEl.querySelector(`input[name="${name}"]:checked`);
        if (!checked) {
          isValid = false;
          radioGroups[name].forEach(radio => {
            const label = radio.closest('.radio-label');
            if (label && isVisible(label)) {
              label.style.setProperty('border-color', '#f04444', 'important');
            }
          });
        } else {
          radioGroups[name].forEach(radio => {
            const label = radio.closest('.radio-label');
            if (label) {
              label.style.removeProperty('border-color');
            }
          });
        }
      });
      
      // Проверка чекбоксов с required (только видимые)
      currentStepEl.querySelectorAll('input[type="checkbox"][required]').forEach(checkbox => {
        if (!isVisible(checkbox)) return; // Пропускаем скрытые поля
        
        if (!checkbox.checked) {
          isValid = false;
          const label = checkbox.closest('label');
          if (label && isVisible(label)) {
            label.style.setProperty('border-color', '#f04444', 'important');
          }
        } else {
          const label = checkbox.closest('label');
          if (label) {
            label.style.removeProperty('border-color');
          }
        }
      });
      
      if (!isValid) {
        showToast('Пожалуйста, заполните все обязательные поля на текущем шаге');
        return;
      }
    }
  }
  
  currentStep = step;
  updateStepDisplay();
}

function fillProfileForm(profile) {
  if (!profile) return;
  
  // Step 1
  if (profileForm.full_name) profileForm.full_name.value = profile.full_name || '';
  if (profileForm.has_self_employment) {
    profileForm.has_self_employment.value = profile.has_self_employment !== null ? String(profile.has_self_employment) : '';
  }
  if (profileForm.ready_for_self_employment) {
    profileForm.ready_for_self_employment.value = profile.ready_for_self_employment || '';
  }
  if (profileForm.main_blog_link) profileForm.main_blog_link.value = profile.main_blog_link || '';
  const container = document.getElementById('social-links-container');
  if (container) {
    container.innerHTML = '';
    if (profile.social_links && Array.isArray(profile.social_links) && profile.social_links.length > 0) {
      profile.social_links.forEach(link => {
        const input = document.createElement('input');
        input.type = 'url';
        input.name = 'social_links[]';
        input.placeholder = 'https://...';
        input.value = link;
        input.required = true;
        container.appendChild(input);
      });
    } else {
      // Создаем хотя бы одно пустое поле
      const input = document.createElement('input');
      input.type = 'url';
      input.name = 'social_links[]';
      input.placeholder = 'https://...';
      input.required = true;
      container.appendChild(input);
    }
  }
  if (profileForm.country) profileForm.country.value = profile.country || '';
  if (profileForm.city) profileForm.city.value = profile.city || '';
  if (profileForm.age) profileForm.age.value = profile.age || '';
  if (profileForm.gender) {
    const genderRadio = profileForm.querySelector(`input[name="gender"][value="${profile.gender}"]`);
    if (genderRadio) genderRadio.checked = true;
  }
  if (profileForm.coverage_regions) profileForm.coverage_regions.value = profile.coverage_regions || '';
  
  // Step 2
  const platformsContainer = document.getElementById('platforms-container');
  if (platformsContainer) {
    platformsContainer.innerHTML = '';
    if (profile.platforms && Array.isArray(profile.platforms) && profile.platforms.length > 0) {
      profile.platforms.forEach(platform => {
        const input = document.createElement('input');
        input.type = 'text';
        input.name = 'platforms[]';
        input.placeholder = 'Например: Instagram';
        input.value = platform;
        input.required = true;
        platformsContainer.appendChild(input);
      });
    } else {
      const input = document.createElement('input');
      input.type = 'text';
      input.name = 'platforms[]';
      input.placeholder = 'Например: Instagram';
      input.required = true;
      platformsContainer.appendChild(input);
    }
  }
  const blogTopicsContainer = document.getElementById('blog-topics-container');
  if (blogTopicsContainer) {
    blogTopicsContainer.innerHTML = '';
    if (profile.blog_topics && Array.isArray(profile.blog_topics) && profile.blog_topics.length > 0) {
      profile.blog_topics.forEach(topic => {
        const input = document.createElement('input');
        input.type = 'text';
        input.name = 'blog_topics[]';
        input.placeholder = 'Например: Косметика';
        input.value = topic;
        input.required = true;
        blogTopicsContainer.appendChild(input);
      });
    } else {
      const input = document.createElement('input');
      input.type = 'text';
      input.name = 'blog_topics[]';
      input.placeholder = 'Например: Косметика';
      input.required = true;
      blogTopicsContainer.appendChild(input);
    }
  }
  if (profileForm.blog_description) profileForm.blog_description.value = profile.blog_description || '';
  if (profileForm.blog_experience) {
    const expRadio = profileForm.querySelector(`input[name="blog_experience"][value="${profile.blog_experience}"]`);
    if (expRadio) expRadio.checked = true;
  }
  if (profileForm.publication_frequency) {
    const freqRadio = profileForm.querySelector(`input[name="publication_frequency"][value="${profile.publication_frequency}"]`);
    if (freqRadio) freqRadio.checked = true;
  }
  
  // Step 3
  const subscribersContainer = document.getElementById('subscribers-container');
  if (subscribersContainer) {
    subscribersContainer.innerHTML = '';
    if (profile.subscribers_by_platform && Array.isArray(profile.subscribers_by_platform) && profile.subscribers_by_platform.length > 0) {
      profile.subscribers_by_platform.forEach(sub => {
        const input = document.createElement('input');
        input.type = 'text';
        input.name = 'subscribers_by_platform[]';
        input.placeholder = 'Платформа: количество';
        input.value = sub;
        input.required = true;
        subscribersContainer.appendChild(input);
      });
    } else {
      const input = document.createElement('input');
      input.type = 'text';
      input.name = 'subscribers_by_platform[]';
      input.placeholder = 'Платформа: количество';
      input.required = true;
      subscribersContainer.appendChild(input);
    }
  }
  const reachContainer = document.getElementById('reach-container');
  if (reachContainer) {
    reachContainer.innerHTML = '';
    if (profile.average_reach && Array.isArray(profile.average_reach) && profile.average_reach.length > 0) {
      profile.average_reach.forEach(reach => {
        const input = document.createElement('input');
        input.type = 'text';
        input.name = 'average_reach[]';
        input.placeholder = 'Канал: охват';
        input.value = reach;
        input.required = true;
        reachContainer.appendChild(input);
      });
    } else {
      const input = document.createElement('input');
      input.type = 'text';
      input.name = 'average_reach[]';
      input.placeholder = 'Канал: охват';
      input.required = true;
      reachContainer.appendChild(input);
    }
  }
  if (profileForm.audience_gender_age) profileForm.audience_gender_age.value = profile.audience_gender_age || '';
  if (profileForm.audience_region) profileForm.audience_region.value = profile.audience_region || '';
  if (profileForm.engagement_level) profileForm.engagement_level.value = profile.engagement_level || '';
  
  // Step 4
  if (profileForm.has_collaborations) {
    profileForm.has_collaborations.checked = profile.has_collaborations || false;
  }
  const collaborationsContainer = document.getElementById('collaborations-container');
  if (collaborationsContainer) {
    collaborationsContainer.innerHTML = '';
    if (profile.collaboration_examples && Array.isArray(profile.collaboration_examples) && profile.collaboration_examples.length > 0) {
      profile.collaboration_examples.forEach(example => {
        const input = document.createElement('input');
        input.type = 'text';
        input.name = 'collaboration_examples[]';
        input.placeholder = 'Кейсы, ссылки, бренды';
        input.value = example;
        collaborationsContainer.appendChild(input);
      });
    } else {
      const input = document.createElement('input');
      input.type = 'text';
      input.name = 'collaboration_examples[]';
      input.placeholder = 'Кейсы, ссылки, бренды';
      collaborationsContainer.appendChild(input);
    }
  }
  if (profileForm.ready_to_share_results) {
    const shareRadio = profileForm.querySelector(`input[name="ready_to_share_results"][value="${profile.ready_to_share_results}"]`);
    if (shareRadio) shareRadio.checked = true;
  }
  if (profileForm.ready_for_paid_ads) {
    const paidRadio = profileForm.querySelector(`input[name="ready_for_paid_ads"][value="${profile.ready_for_paid_ads}"]`);
    if (paidRadio) paidRadio.checked = true;
  }
  
  // Step 5
  const formatsContainer = document.getElementById('formats-container');
  if (formatsContainer) {
    formatsContainer.innerHTML = '';
    if (profile.collaboration_formats && Array.isArray(profile.collaboration_formats) && profile.collaboration_formats.length > 0) {
      profile.collaboration_formats.forEach(format => {
        const input = document.createElement('input');
        input.type = 'text';
        input.name = 'collaboration_formats[]';
        input.value = format;
        input.required = true;
        formatsContainer.appendChild(input);
      });
    } else {
      const input = document.createElement('input');
      input.type = 'text';
      input.name = 'collaboration_formats[]';
      input.required = true;
      formatsContainer.appendChild(input);
    }
  }
  const pricingContainer = document.getElementById('pricing-container');
  if (pricingContainer) {
    pricingContainer.innerHTML = '';
    if (profile.ad_pricing && Array.isArray(profile.ad_pricing) && profile.ad_pricing.length > 0) {
      profile.ad_pricing.forEach(pricing => {
        const input = document.createElement('input');
        input.type = 'text';
        input.name = 'ad_pricing[]';
        input.placeholder = 'Соцсеть, тип - стоимость';
        input.value = pricing;
        input.required = true;
        pricingContainer.appendChild(input);
      });
    } else {
      const input = document.createElement('input');
      input.type = 'text';
      input.name = 'ad_pricing[]';
      input.placeholder = 'Соцсеть, тип - стоимость';
      input.required = true;
      pricingContainer.appendChild(input);
    }
  }
  if (profileForm.ready_for_barter) {
    const barterRadio = profileForm.querySelector(`input[name="ready_for_barter"][value="${profile.ready_for_barter}"]`);
    if (barterRadio) barterRadio.checked = true;
  }
  const barterCategoriesContainer = document.getElementById('barter-categories-container');
  if (barterCategoriesContainer) {
    barterCategoriesContainer.innerHTML = '';
    if (profile.barter_categories && Array.isArray(profile.barter_categories) && profile.barter_categories.length > 0) {
      profile.barter_categories.forEach(category => {
        const input = document.createElement('input');
        input.type = 'text';
        input.name = 'barter_categories[]';
        input.value = category;
        input.required = true;
        barterCategoriesContainer.appendChild(input);
      });
    } else {
      const input = document.createElement('input');
      input.type = 'text';
      input.name = 'barter_categories[]';
      input.required = true;
      barterCategoriesContainer.appendChild(input);
    }
  }
  
  // Step 6
  if (profileForm.ready_for_brand_projects) {
    const brandRadio = profileForm.querySelector(`input[name="ready_for_brand_projects"][value="${profile.ready_for_brand_projects}"]`);
    if (brandRadio) brandRadio.checked = true;
  }
  if (profileForm.products_wont_advertise) profileForm.products_wont_advertise.value = profile.products_wont_advertise || '';
  if (profileForm.blog_management) {
    const mgmtRadio = profileForm.querySelector(`input[name="blog_management"][value="${profile.blog_management}"]`);
    if (mgmtRadio) mgmtRadio.checked = true;
  }
  if (profileForm.has_media_kit) {
    profileForm.has_media_kit.value = profile.has_media_kit !== null ? String(profile.has_media_kit) : '';
    toggleMediaKitLink(profileForm.has_media_kit);
  }
  if (profileForm.media_kit_link) profileForm.media_kit_link.value = profile.media_kit_link || '';
  if (profileForm.ready_for_blogger_community) {
    const commRadio = profileForm.querySelector(`input[name="ready_for_blogger_community"][value="${profile.ready_for_blogger_community}"]`);
    if (commRadio) commRadio.checked = true;
  }
  if (profileForm.additional_info) profileForm.additional_info.value = profile.additional_info || '';
  if (profileForm.consent_privacy) profileForm.consent_privacy.checked = profile.consent_privacy || false;
  if (profileForm.consent_marketing_email) profileForm.consent_marketing_email.checked = profile.consent_marketing_email || false;
  if (profileForm.consent_marketing_calls) profileForm.consent_marketing_calls.checked = profile.consent_marketing_calls || false;
  
  // Legacy fields
  if (profileForm.contact) profileForm.contact.value = profile.contact || '';
  if (profileForm.date_of_birth) profileForm.date_of_birth.value = profile.date_of_birth || '';
  if (profileForm.pickup_point) profileForm.pickup_point.value = profile.pickup_point || '';
  
  if (profileStatus) {
    profileStatus.textContent = profile.is_completed
      ? 'Профиль заполнен ✅'
      : 'Заполните все обязательные поля, чтобы участвовать в заказах.';
  }
  if (participationBtn) {
    participationBtn.dataset.active = String(profile.is_participating);
    participationBtn.textContent = profile.is_participating ? 'Остановить участие' : 'Участвовать в заказах';
  }
}

async function loadOrders() {
  const orders = await apiRequest('/orders/creating/');
  state.orders = orders;
  renderOrders();
}

async function loadPurchases() {
  try {
    const purchases = await apiRequest('/orders/purchases/');
    state.purchases = purchases || [];
    renderPurchases();
  } catch (error) {
    console.warn('Не удалось загрузить заказы:', error);
    state.purchases = [];
    renderPurchases();
  }
}

function renderOrders() {
  ordersList.innerHTML = '';
  if (!state.orders.length) {
    ordersList.innerHTML = '<li>Нет заказов для подтверждения.</li>';
    return;
  }

  state.orders.forEach((order) => {
    const li = document.createElement('li');
    li.classList.add('order-card');
    li.innerHTML = `
      <div><strong>Артикул:</strong> ${order.article}</div>
      ${order.title ? `<div><strong>Название:</strong> ${order.title}</div>` : ''}
      <div><strong>ПВЗ:</strong> ${order.pickup_point || '—'}</div>
      <div><strong>Описание:</strong> ${order.notes || '—'}</div>
      <pre>${JSON.stringify(order.payload || {}, null, 2)}</pre>
      <div class="order-card-actions">
        <button data-action="approve" data-id="${order.id}">Принять</button>
        <button data-action="reject" data-id="${order.id}">Отклонить</button>
      </div>
    `;
    ordersList.appendChild(li);
  });
}

function renderPurchases() {
  purchasesList.innerHTML = '';
  if (!state.purchases.length) {
    purchasesList.innerHTML = '<li>Пока нет активных заказов.</li>';
    return;
  }

  state.purchases.forEach((purchase) => {
    const li = document.createElement('li');
    li.classList.add('purchase-card');
    li.innerHTML = `
      <div><strong>Артикул:</strong> ${purchase.article}</div>
      <div><strong>ID:</strong> ${purchase.external_id || '—'}</div>
      <div><strong>ПВЗ:</strong> ${purchase.pickup_point || '—'}</div>
      <div><strong>Статус:</strong> ${purchase.status}</div>
      <pre>${JSON.stringify(purchase.metadata || {}, null, 2)}</pre>
    `;
    purchasesList.appendChild(li);
  });
}

// Helper functions for adding fields
function addSocialLink() {
  const container = document.getElementById('social-links-container');
  if (container) {
    const input = document.createElement('input');
    input.type = 'url';
    input.name = 'social_links[]';
    input.placeholder = 'https://...';
    input.required = true;
    container.appendChild(input);
  }
}

function addPlatform() {
  const container = document.getElementById('platforms-container');
  if (container) {
    const input = document.createElement('input');
    input.type = 'text';
    input.name = 'platforms[]';
    input.placeholder = 'Например: Instagram';
    input.required = true;
    container.appendChild(input);
  }
}

function addBlogTopic() {
  const container = document.getElementById('blog-topics-container');
  if (container) {
    const input = document.createElement('input');
    input.type = 'text';
    input.name = 'blog_topics[]';
    input.placeholder = 'Например: Косметика';
    input.required = true;
    container.appendChild(input);
  }
}

function addSubscriber() {
  const container = document.getElementById('subscribers-container');
  if (container) {
    const input = document.createElement('input');
    input.type = 'text';
    input.name = 'subscribers_by_platform[]';
    input.placeholder = 'Платформа: количество';
    input.required = true;
    container.appendChild(input);
  }
}

function addReach() {
  const container = document.getElementById('reach-container');
  if (container) {
    const input = document.createElement('input');
    input.type = 'text';
    input.name = 'average_reach[]';
    input.placeholder = 'Канал: охват';
    input.required = true;
    container.appendChild(input);
  }
}

function addCollaboration() {
  const container = document.getElementById('collaborations-container');
  if (container) {
    const input = document.createElement('input');
    input.type = 'text';
    input.name = 'collaboration_examples[]';
    input.placeholder = 'Кейсы, ссылки, бренды';
    container.appendChild(input);
  }
}

function addFormat() {
  const container = document.getElementById('formats-container');
  if (container) {
    const input = document.createElement('input');
    input.type = 'text';
    input.name = 'collaboration_formats[]';
    input.required = true;
    container.appendChild(input);
  }
}

function addPricing() {
  const container = document.getElementById('pricing-container');
  if (container) {
    const input = document.createElement('input');
    input.type = 'text';
    input.name = 'ad_pricing[]';
    input.placeholder = 'Соцсеть, тип - стоимость';
    input.required = true;
    container.appendChild(input);
  }
}

function addBarterCategory() {
  const container = document.getElementById('barter-categories-container');
  if (container) {
    const input = document.createElement('input');
    input.type = 'text';
    input.name = 'barter_categories[]';
    input.required = true;
    container.appendChild(input);
  }
}

function toggleMediaKitLink(select) {
  const label = document.getElementById('media-kit-link-label');
  const input = profileForm.media_kit_link;
  if (select.value === 'true') {
    if (label) label.classList.remove('hidden');
    if (input) input.required = true;
  } else {
    if (label) label.classList.add('hidden');
    if (input) {
      input.required = false;
      input.value = '';
    }
  }
}

// Make functions global for onclick handlers
window.addSocialLink = addSocialLink;
window.addPlatform = addPlatform;
window.addBlogTopic = addBlogTopic;
window.addSubscriber = addSubscriber;
window.addReach = addReach;
window.addCollaboration = addCollaboration;
window.addFormat = addFormat;
window.addPricing = addPricing;
window.addBarterCategory = addBarterCategory;
window.toggleMediaKitLink = toggleMediaKitLink;

// Navigation buttons
document.getElementById('prev-step-btn')?.addEventListener('click', () => {
  goToStep(currentStep - 1);
});

document.getElementById('next-step-btn')?.addEventListener('click', () => {
  goToStep(currentStep + 1);
});

profileForm.addEventListener('submit', async (event) => {
  event.preventDefault();
  
  const submitBtn = document.getElementById('submit-btn');
  const originalText = submitBtn ? submitBtn.textContent : 'Отправить';
  
  // Показываем индикатор загрузки
  if (submitBtn) {
    submitBtn.disabled = true;
    submitBtn.textContent = 'Сохранение...';
  }
  
  try {
    
    const formData = new FormData(profileForm);
    
    const getTrimmed = (name) => {
      const value = formData.get(name);
      return value === null || value === undefined ? '' : String(value).trim();
    };
    
    const getAll = (name) => {
      return formData.getAll(name).map(v => String(v).trim()).filter(v => v);
    };

    const payload = {
      // Step 1
      full_name: getTrimmed('full_name'),
      has_self_employment: getTrimmed('has_self_employment') === 'true' ? true : (getTrimmed('has_self_employment') === 'false' ? false : null),
      ready_for_self_employment: getTrimmed('ready_for_self_employment'),
      main_blog_link: getTrimmed('main_blog_link'),
      social_links: getAll('social_links[]'),
      country: getTrimmed('country'),
      city: getTrimmed('city'),
      age: getTrimmed('age') ? parseInt(getTrimmed('age'), 10) : null,
      gender: getTrimmed('gender'),
      coverage_regions: getTrimmed('coverage_regions'),
      
      // Step 2
      platforms: getAll('platforms[]'),
      blog_topics: getAll('blog_topics[]'),
      blog_description: getTrimmed('blog_description'),
      blog_experience: getTrimmed('blog_experience'),
      publication_frequency: getTrimmed('publication_frequency'),
      
      // Step 3
      subscribers_by_platform: getAll('subscribers_by_platform[]'),
      average_reach: getAll('average_reach[]'),
      audience_gender_age: getTrimmed('audience_gender_age'),
      audience_region: getTrimmed('audience_region'),
      engagement_level: getTrimmed('engagement_level'),
      
      // Step 4
      has_collaborations: formData.get('has_collaborations') === 'on',
      collaboration_examples: getAll('collaboration_examples[]'),
      ready_to_share_results: getTrimmed('ready_to_share_results'),
      ready_for_paid_ads: getTrimmed('ready_for_paid_ads'),
      
      // Step 5
      collaboration_formats: getAll('collaboration_formats[]'),
      ad_pricing: getAll('ad_pricing[]'),
      ready_for_barter: getTrimmed('ready_for_barter'),
      barter_categories: getAll('barter_categories[]'),
      
      // Step 6
      ready_for_brand_projects: getTrimmed('ready_for_brand_projects'),
      products_wont_advertise: getTrimmed('products_wont_advertise'),
      blog_management: getTrimmed('blog_management'),
      has_media_kit: getTrimmed('has_media_kit') === 'true' ? true : (getTrimmed('has_media_kit') === 'false' ? false : null),
      media_kit_link: getTrimmed('media_kit_link'),
      ready_for_blogger_community: getTrimmed('ready_for_blogger_community'),
      additional_info: getTrimmed('additional_info'),
      consent_privacy: formData.get('consent_privacy') === 'on',
      consent_marketing_email: formData.get('consent_marketing_email') === 'on',
      consent_marketing_calls: formData.get('consent_marketing_calls') === 'on',
      
      // Legacy fields
      contact: getTrimmed('contact'),
      date_of_birth: getTrimmed('date_of_birth') || null,
      pickup_point: getTrimmed('pickup_point'),
    };

    console.log('Отправка данных профиля:', payload);

    const profile = await apiRequest('/profile/me/', {
      method: 'PATCH',
      body: JSON.stringify(payload),
    });
    
    console.log('Профиль сохранен:', profile);
    
    state.profile = profile;
    fillProfileForm(profile);
    showToast('Профиль успешно сохранён! ✅');
    goToStep(1); // Reset to first step after save
    
    // Перезагружаем данные профиля
    await loadProfile();
    
  } catch (error) {
    console.error('Ошибка при сохранении профиля:', error);
    
    // Пытаемся извлечь детали ошибки
    let errorMessage = 'Ошибка сохранения профиля';
    if (error.message) {
      errorMessage = error.message;
      // Если это JSON с ошибками валидации
      try {
        const errorData = JSON.parse(error.message);
        if (errorData && typeof errorData === 'object') {
          const errors = Object.entries(errorData)
            .map(([field, messages]) => `${field}: ${Array.isArray(messages) ? messages.join(', ') : messages}`)
            .join('; ');
          errorMessage = `Ошибки валидации: ${errors}`;
        }
      } catch (e) {
        // Не JSON, используем как есть
      }
    }
    
    showToast(errorMessage);
    alert(`Ошибка: ${errorMessage}\n\nПроверьте консоль браузера (F12) для деталей.`);
  } finally {
    // Восстанавливаем кнопку
    if (submitBtn) {
      submitBtn.disabled = false;
      submitBtn.textContent = originalText;
    }
  }
});

participationBtn.addEventListener('click', async () => {
  if (!state.profile) {
    return;
  }
  const nextState = participationBtn.dataset.active !== 'true';

  try {
    const profile = await apiRequest('/profile/participation/', {
      method: 'POST',
      body: JSON.stringify({ is_participating: nextState }),
    });
    state.profile = profile;
    fillProfileForm(profile);
    showToast(nextState ? 'Вы включили участие в заказах.' : 'Вы остановили участие.');
    await loadOrders();
  } catch (error) {
    console.error(error);
    showToast(`Не удалось изменить участие: ${error.message}`);
  }
});

ordersList.addEventListener('click', async (event) => {
  if (!(event.target instanceof HTMLButtonElement)) {
    return;
  }

  const action = event.target.dataset.action;
  const id = event.target.dataset.id;

  if (!action || !id) {
    return;
  }

  const payload = { action };
  if (action === 'approve') {
    payload.external_id = prompt('Введите ID заказа (можно оставить пустым)', '') || '';
    payload.pickup_point = prompt('Введите ПВЗ (по умолчанию из профиля)', '') || '';
  }

  try {
    await apiRequest(`/orders/creating/${id}/decision/`, {
      method: 'POST',
      body: JSON.stringify(payload),
    });
    showToast(action === 'approve' ? 'Заказ принят.' : 'Заказ отклонён.');
    await Promise.all([loadOrders(), loadPurchases()]);
  } catch (error) {
    console.error(error);
    showToast(`Ошибка обработки заказа: ${error.message}`);
  }
});

if (navProfileBtn) {
  navProfileBtn.addEventListener('click', () => {
    profileSection?.classList.remove('hidden');
    profileSection?.scrollIntoView({ behavior: 'smooth', block: 'start' });
  });
}

navShowLogin?.addEventListener('click', () => {
  showAuthForm('login');
  loginSection?.scrollIntoView({ behavior: 'smooth', block: 'start' });
  showToast('Открыта форма входа');
});

navShowRegister?.addEventListener('click', () => {
  showAuthForm('register');
  registrationSection?.scrollIntoView({ behavior: 'smooth', block: 'start' });
  showToast('Открыта форма регистрации');
});

// Initialize multi-step form
updateStepDisplay();

setAuthState({ token: null, user: null });
showAuthForm(currentAuthView);

