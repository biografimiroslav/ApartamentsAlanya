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

// Typewriter effect
function initTypewriter() {
  const words = ["ПРИВАБЛИВИХ", "СУЧАСНИХ", "КОМФОРТНИХ", "СТИЛЬНИХ", "ЗРУЧНИХ", "ПРОСТОРИХ", "ЕЛЕГАНТНИХ"];
  const wordSpan = document.querySelector(".word");

  let wordIndex = 0;
  let charIndex = 0;
  let deleting = false;
  let delay = 100;

  function type() {
    const currentWord = words[wordIndex];

    if (!deleting) {
      wordSpan.textContent = currentWord.slice(0, charIndex + 1);
      charIndex++;

      if (charIndex === currentWord.length) {
        deleting = true;
        setTimeout(type, 1000);
        return;
      }
    } else {
      wordSpan.textContent = currentWord.slice(0, charIndex - 1);
      charIndex--;

      if (charIndex === 0) {
        deleting = false;
        wordIndex = (wordIndex + 1) % words.length;
      }
    }

    setTimeout(type, deleting ? 50 : delay);
  }

  type();
}

// Apartment sliders
function initSliders() {
  document.querySelectorAll('.apartamentSlider').forEach(slider => {
    const slides = slider.querySelectorAll('.apartamentIMG');
    let current = 0;

    function showSlide(index) {
      slides.forEach((img, i) => {
        img.classList.toggle('active', i === index);
      });
    }

    slider.querySelector('.prev').addEventListener('click', () => {
      current = (current - 1 + slides.length) % slides.length;
      showSlide(current);
    });

    slider.querySelector('.next').addEventListener('click', () => {
      current = (current + 1) % slides.length;
      showSlide(current);
    });
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

// Call enhanced hover effects
enhanceHoverEffects();
