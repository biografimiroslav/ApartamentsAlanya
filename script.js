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
  console.log('Initializing sliders...');

  document.querySelectorAll('.apartamentSlider').forEach((slider, sliderIndex) => {
    const slides = slider.querySelectorAll('.apartamentIMG');
    const prevBtn = slider.querySelector('.prev');
    const nextBtn = slider.querySelector('.next');

    console.log(`Slider ${sliderIndex + 1}: Found ${slides.length} slides`);

    if (slides.length === 0) {
      console.warn(`Slider ${sliderIndex + 1}: No slides found`);
      return; 
    }

    let current = 0;

    // Initialize first slide as active
    showSlide(current);

    function showSlide(index) {
      // Find current active slide
      const currentActive = slider.querySelector('.apartamentIMG.active');

      if (currentActive) {
        // Add fade-out class to current active slide
        currentActive.classList.add('fade-out');

        // Wait for fade-out animation to complete, then switch slides
        setTimeout(() => {
          // Remove active and fade-out classes from all slides
          slides.forEach((img) => {
            img.classList.remove('active', 'fade-out');
          });

          // Add active class to new slide
          slides[index].classList.add('active');
          console.log(`Slider ${sliderIndex + 1}: Showing slide ${index + 1}/${slides.length}`);
        }, 1); // Match the fade-out animation duration (0.8s)
      } else {
        // No current active slide, just activate the new one
        slides.forEach((img, i) => {
          if (i === index) {
            img.classList.add('active');
          } else {
            img.classList.remove('active');
          }
        });
        console.log(`Slider ${sliderIndex + 1}: Showing slide ${index + 1}/${slides.length}`);
      }
    }

    // Add event listeners with null checks
    if (prevBtn) {
      prevBtn.addEventListener('click', (e) => {
        e.preventDefault();
        current = (current - 1 + slides.length) % slides.length;
        showSlide(current);
      });
    } else {
      console.warn(`Slider ${sliderIndex + 1}: Previous button not found`);
    }

    if (nextBtn) {
      nextBtn.addEventListener('click', (e) => {
        e.preventDefault();
        current = (current + 1) % slides.length;
        showSlide(current);
      });
    } else {
      console.warn(`Slider ${sliderIndex + 1}: Next button not found`);
    }

    // Auto-play functionality (optional)
    let autoPlayInterval = setInterval(() => {
      current = (current + 1) % slides.length;
      showSlide(current);
    }, 5000); // Change slide every 5 seconds

    // Pause auto-play on hover
    slider.addEventListener('mouseenter', () => {
      clearInterval(autoPlayInterval);
    });

    // Resume auto-play when mouse leaves
    slider.addEventListener('mouseleave', () => {
      autoPlayInterval = setInterval(() => {
        current = (current + 1) % slides.length;
        showSlide(current);
      }, 5000);
    });
  });

  console.log('Sliders initialization complete');
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
