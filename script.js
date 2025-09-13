// Animation and functionality script
document.addEventListener('DOMContentLoaded', function() {
  console.log("Script loaded successfully.");
  
  // Initialize animations
  initAnimations();
  
  // Add scroll event listener for scroll-based animations
  window.addEventListener('scroll', handleScrollAnimations);
  
  // Trigger initial animations
  setTimeout(() => {
    animateOnLoad();
  }, 100);
  
  // Initialize existing functionality
  initTypewriter();
  initSliders();
  initReviewsSlider();

  // Initialize Telegram form handler
  // initTelegramForm(); // Disabled because function is not defined

  // Load prices from database
  loadPricesFromDatabase();

  // Load phone number from database
  loadPhoneFromDatabase();

  // Load reviews from database
  loadReviewsFromDatabase();
});

// Animation functions
function initAnimations() {
  // Add animation classes to elements
  const animatedElements = document.querySelectorAll('.header-content, .aboutContent, .apartamentSlider, .reviewsContent, .quick-booking, .contact-card');
  animatedElements.forEach(el => {
    el.style.opacity = '0';
    el.style.transform = 'translateY(30px)';
    el.style.transition = 'opacity 0.8s ease, transform 0.8s ease';
  });
}

function animateOnLoad() {
  // Animate header content
  const headerContent = document.querySelector('.header-content');
  if (headerContent) {
    headerContent.style.opacity = '1';
    headerContent.style.transform = 'translateY(0)';
  }
  
  // Animate video background with slight zoom
  const video = document.querySelector('.background-video');
  if (video) {
    video.style.transform = 'scale(1.05)';
    video.style.transition = 'transform 2s ease-out';
    setTimeout(() => {
      video.style.transform = 'scale(1)';
    }, 100);
  }
}

function handleScrollAnimations() {
  const elements = document.querySelectorAll('.aboutContent, .apartamentSlider, .reviewsContent, .quick-booking, .contact-card');
  
  elements.forEach(el => {
    const elementTop = el.getBoundingClientRect().top;
    const elementBottom = el.getBoundingClientRect().bottom;
    const windowHeight = window.innerHeight;
    
    if (elementTop < windowHeight * 0.8 && elementBottom > 0) {
      el.style.opacity = '1';
      el.style.transform = 'translateY(0)';
    }
  });
}

// Enhanced hover effects
function enhanceHoverEffects() {
  const buttons = document.querySelectorAll('button');
  buttons.forEach(btn => {
    btn.addEventListener('mouseenter', () => {
      btn.style.transform = 'scale(1.05)';
      btn.style.transition = 'transform 0.3s ease';
    });
    btn.addEventListener('mouseleave', () => {
      btn.style.transform = 'scale(1)';
    });
  });
}



// Apartment sliders
function initSliders() {
  const sliders = document.querySelectorAll('.apartamentSlider');
  if (!sliders.length) return;

  sliders.forEach((slider, sliderIndex) => {
    const slides = Array.from(slider.querySelectorAll('.apartamentIMG'));
    const prevBtn = slider.querySelector('.prev');
    const nextBtn = slider.querySelector('.next');

    if (!slides.length) return;

    // знайти початковий активний слайд або 0
    let current = slides.findIndex(s => s.classList.contains('active'));
    if (current < 0) current = 0;
    slides.forEach((s, i) => s.dataset.idx = i); // мінімізує подальші запити

    const showSlide = (index) => {
      index = (index + slides.length) % slides.length;
      if (index === current) return; // нічого не міняємо якщо той самий
      const prev = slides[current];
      const next = slides[index];

      // Якщо є попередній активний — робимо fade-out, чекаємо transitionend, потім cleanup
      if (prev) {
        prev.classList.remove('active');
        prev.classList.add('fade-out');
        // Встановимо will-change перед анімацією (потім видалимо)
        prev.style.willChange = 'opacity, transform';
        const onEnd = () => {
          prev.classList.remove('fade-out');
          prev.style.willChange = '';
          prev.removeEventListener('transitionend', onEnd);
        };
        prev.addEventListener('transitionend', onEnd, { once: true });
      }

      // Включаємо новий слайд
      next.classList.add('active');
      // для плавності: встановимо will-change і приберемо після першого transitionend
      next.style.willChange = 'opacity, transform';
      const onNextEnd = () => {
        next.style.willChange = '';
        next.removeEventListener('transitionend', onNextEnd);
      };
      next.addEventListener('transitionend', onNextEnd, { once: true });

      current = index;
    };

    // Кнопки
    if (prevBtn) prevBtn.addEventListener('click', (e) => { e.preventDefault(); showSlide(current - 1); });
    if (nextBtn) nextBtn.addEventListener('click', (e) => { e.preventDefault(); showSlide(current + 1); });

    // Автоплей (локальний таймер на кожен слайдер)
    let autoPlayInterval = null;
    const startAutoplay = (interval = 5000) => {
      if (autoPlayInterval) return;
      autoPlayInterval = setInterval(() => showSlide(current + 1), interval);
    };
    const stopAutoplay = () => {
      if (!autoPlayInterval) return;
      clearInterval(autoPlayInterval);
      autoPlayInterval = null;
    };

    // Пауза на hover / resume on leave
    slider.addEventListener('mouseenter', stopAutoplay, { passive: true });
    slider.addEventListener('mouseleave', () => startAutoplay(5000), { passive: true });

    // Опціонально: зупиняти автоплей, якщо слайдер не видно — економить ресурси
    if ('IntersectionObserver' in window) {
      const visObserver = new IntersectionObserver((entries) => {
        entries.forEach(en => {
          if (en.isIntersecting) startAutoplay(5000);
          else stopAutoplay();
        });
      }, { threshold: 0.25 });
      visObserver.observe(slider);
    } else {
      // fallback: завжди вмикаємо
      startAutoplay(5000);
    }

    // Ініціалізація: покажемо початковий слайд (переконаємось, що є active)
    slides.forEach((s, i) => s.classList.toggle('active', i === current));
  });
}


// Reviews slider
function initReviewsSlider() {
  const reviewsList = document.querySelector(".reviewsList");
  const reviewsItems = document.querySelectorAll(".reviewsItem");
  const prevBtn = document.getElementById("prevBtn");
  const nextBtn = document.getElementById("nextBtn");

  let currentIndex = 0;
  const visibleCount = 3;
  const itemWidth = reviewsItems[0].offsetWidth + 20;

  function updateSlider() {
    reviewsList.style.transform = `translateX(-${currentIndex * itemWidth}px)`;
  }

  nextBtn.addEventListener("click", () => {
    if (currentIndex < reviewsItems.length - visibleCount) {
      currentIndex += 1;
      updateSlider();
    }
  });

  prevBtn.addEventListener("click", () => {
    if (currentIndex > 0) {
      currentIndex -= 1;
      updateSlider();
    }
  });
}


// Function to detect current language
function getCurrentLanguage() {
  const path = window.location.pathname;
  if (path.includes('indexUA.html')) return 'ua';
  if (path.includes('indexCZ.html')) return 'cz';
  if (path.includes('indexTR.html')) return 'tr';
  if (path.includes('indexRU.html')) return 'ru';
  return 'en'; // default to English
}

// Function to load prices from database
function loadPricesFromDatabase() {
  const lang = getCurrentLanguage();
  fetch('/api/prices?lang=' + lang)
    .then(response => response.json())
    .then(data => {
      // Update apartment prices on the page
      updateApartmentPrices(data);
    })
    .catch(error => {
      console.error('Error loading prices:', error);
      // Prices will remain as default values if API fails
    });
}

// Function to load phone number from database
function loadPhoneFromDatabase() {
  fetch('/api/phone')
    .then(response => response.json())
    .then(data => {
      // Update phone number on the page
      updatePhoneNumber(data.phone_number);
    })
    .catch(error => {
      console.error('Error loading phone:', error);
      // Phone will remain as default value if API fails
    });
}

// Function to load reviews from database
function loadReviewsFromDatabase() {
  fetch('/api/reviews')
    .then(response => response.json())
    .then(data => {
      // Update reviews on the page
      updateReviews(data.reviews);
    })
    .catch(error => {
      console.error('Error loading reviews:', error);
      // Reviews will remain as default values if API fails
    });
}

// Function to update apartment prices in HTML
function updateApartmentPrices(prices) {
  // Update apartment prices by data attribute
  const priceElements = document.querySelectorAll('.apartamentPrice, .apartamentPrice1');
  priceElements.forEach((element) => {
    const apartmentNumber = element.getAttribute('data-apartment');
    if (apartmentNumber === '1') {
      element.textContent = prices.apartament1;
    } else if (apartmentNumber === '2') {
      element.textContent = prices.apartament2;
    } else if (apartmentNumber === '3') {
      element.textContent = prices.apartament3;
    } else {
      // fallback if no data attribute
      element.textContent = prices.apartament1;
    }
  });

  // Also update prices in the quick booking select options
  const apartmentSelect = document.getElementById('qb-apartment');
  if (apartmentSelect) {
    for (let option of apartmentSelect.options) {
      if (option.value === 'apartment1') {
        option.text = `Квартира 1 — ${prices.apartament1}`;
        // Extract numeric price for data-price attribute
        const price1 = prices.apartament1.replace(/[^\d]/g, '');
        option.setAttribute('data-price', price1);
      } else if (option.value === 'apartment2') {
        option.text = `Квартира 2 — ${prices.apartament2}`;
        // Extract numeric price for data-price attribute
        const price2 = prices.apartament2.replace(/[^\d]/g, '');
        option.setAttribute('data-price', price2);
      } else if (option.value === 'apartment3') {
        option.text = `Квартира 3 — ${prices.apartament3}`;
        // Extract numeric price for data-price attribute
        const price3 = prices.apartament3.replace(/[^\d]/g, '');
        option.setAttribute('data-price', price3);
      }
    }
  }
}

// Call enhanced hover effects
enhanceHoverEffects();


// Language dropdown functionality
document.addEventListener('DOMContentLoaded', () => {
  const selectedLang = document.querySelector('.selectedLang');
  const langDropdown = document.querySelector('.langDropdown');

  if (selectedLang && langDropdown) {
    selectedLang.addEventListener('click', (e) => {
      e.preventDefault();
      langDropdown.classList.toggle('open');
    });

    // Close dropdown when clicking outside
    document.addEventListener('click', (e) => {
      if (!selectedLang.contains(e.target) && !langDropdown.contains(e.target)) {
        langDropdown.classList.remove('open');
      }
    });

    // Handle language selection
    const langItems = langDropdown.querySelectorAll('li');
    langItems.forEach(item => {
      item.addEventListener('click', () => {
        // Update selected language display
        const selectedImg = selectedLang.querySelector('img');
        const selectedText = selectedLang.querySelector('p');
        const itemImg = item.querySelector('img');
        const itemText = item.querySelector('p').textContent.trim();

        if (selectedImg && itemImg) {
          selectedImg.src = itemImg.src;
        }
        if (selectedText) {
          selectedText.textContent = itemText;
        }

        // Close dropdown
        langDropdown.classList.remove('open');
      });
    });
  }
});

// Function to update phone number in HTML
function updatePhoneNumber(phoneNumber) {
  // Update phone number in quick booking
  const phoneElements = document.querySelectorAll('.booking-phone');
  phoneElements.forEach(element => {
    element.textContent = phoneNumber;
    element.href = 'tel:' + phoneNumber.replace(/\s+/g, '');
  });
}

// Function to update reviews in HTML
function updateReviews(reviews) {
  // Update reviews in the reviews section
  const reviewsContainer = document.querySelector('.reviewsList');
  if (reviewsContainer && reviews.length > 0) {
    // Clear existing reviews
    reviewsContainer.innerHTML = '';

    // Add new reviews
    reviews.forEach(review => {
      const reviewItem = document.createElement('div');
      reviewItem.className = 'reviewsItem';
      reviewItem.innerHTML = `
        <p class="reviewsText">${review}</p>
      `;
      reviewsContainer.appendChild(reviewItem);
    });

    // Reinitialize reviews slider after updating content
    initReviewsSlider();
  }
}

// FAQ toggle functionality with smooth animations
document.addEventListener('DOMContentLoaded', () => {
  const faqButtons = document.querySelectorAll('.faq-question');
  faqButtons.forEach(button => {
    button.addEventListener('click', () => {
      const expanded = button.getAttribute('aria-expanded') === 'true';
      button.setAttribute('aria-expanded', !expanded);

      const answerId = button.getAttribute('aria-controls');
      const answer = document.getElementById(answerId);

      if (answer) {
        if (expanded) {
          // Collapse
          answer.classList.remove('faq-answer-expanded');
        } else {
          // Expand
          answer.classList.add('faq-answer-expanded');
        }
      }
    });
  });
});
