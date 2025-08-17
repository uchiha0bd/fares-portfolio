/**
* Template Name: MyResume
* Template URL: https://bootstrapmade.com/free-html-bootstrap-template-my-resume/
* Updated: Jun 29 2024 with Bootstrap v5.3.3
* Author: BootstrapMade.com
* License: https://bootstrapmade.com/license/
*/

(function() {
  "use strict";

  /**
   * Header toggle
   */
  const headerToggleBtn = document.querySelector('.header-toggle');

  function headerToggle() {
    document.querySelector('#header').classList.toggle('header-show');
    headerToggleBtn.classList.toggle('bi-list');
    headerToggleBtn.classList.toggle('bi-x');
  }
  headerToggleBtn.addEventListener('click', headerToggle);

  /**
   * Hide mobile nav on same-page/hash links
   */
  document.querySelectorAll('#navmenu a').forEach(navmenu => {
    navmenu.addEventListener('click', () => {
      if (document.querySelector('.header-show')) {
        headerToggle();
      }
    });

  });

  /**
   * Toggle mobile nav dropdowns
   */
  document.querySelectorAll('.navmenu .toggle-dropdown').forEach(navmenu => {
    navmenu.addEventListener('click', function(e) {
      e.preventDefault();
      this.parentNode.classList.toggle('active');
      this.parentNode.nextElementSibling.classList.toggle('dropdown-active');
      e.stopImmediatePropagation();
    });
  });

  /**
   * Preloader
   */
  const preloader = document.querySelector('#preloader');
  if (preloader) {
    window.addEventListener('load', () => {
      preloader.remove();
    });
  }

  /**
   * Scroll top button
   */
  let scrollTop = document.querySelector('.scroll-top');

  function toggleScrollTop() {
    if (scrollTop) {
      window.scrollY > 100 ? scrollTop.classList.add('active') : scrollTop.classList.remove('active');
    }
  }
  scrollTop.addEventListener('click', (e) => {
    e.preventDefault();
    window.scrollTo({
      top: 0,
      behavior: 'smooth'
    });
  });

  window.addEventListener('load', toggleScrollTop);
  document.addEventListener('scroll', toggleScrollTop);

  /**
   * Animation on scroll function and init
   */
  function aosInit() {
    AOS.init({
      duration: 600,
      easing: 'ease-in-out',
      once: true,
      mirror: false
    });
  }
  window.addEventListener('load', aosInit);

  /**
   * Init typed.js
   */
  const selectTyped = document.querySelector('.typed');
  if (selectTyped) {
    let typed_strings = selectTyped.getAttribute('data-typed-items');
    typed_strings = typed_strings.split(',');
    new Typed('.typed', {
      strings: typed_strings,
      loop: true,
      typeSpeed: 100,
      backSpeed: 50,
      backDelay: 2000
    });
  }

  /**
   * Initiate Pure Counter
   */
  new PureCounter();

  /**
   * Animate the skills items on reveal
   */
  let skillsAnimation = document.querySelectorAll('.skills-animation');
  skillsAnimation.forEach((item) => {
    new Waypoint({
      element: item,
      offset: '80%',
      handler: function(direction) {
        let progress = item.querySelectorAll('.progress .progress-bar');
        progress.forEach(el => {
          el.style.width = el.getAttribute('aria-valuenow') + '%';
        });
      }
    });
  });

  /**
   * Initiate glightbox
   */
  const glightbox = GLightbox({
    selector: '.glightbox'
  });

  /**
   * Init isotope layout and filters
   */
  document.querySelectorAll('.isotope-layout').forEach(function(isotopeItem) {
    let layout = isotopeItem.getAttribute('data-layout') ?? 'masonry';
    let filter = isotopeItem.getAttribute('data-default-filter') ?? '*';
    let sort = isotopeItem.getAttribute('data-sort') ?? 'original-order';

    let initIsotope;
    imagesLoaded(isotopeItem.querySelector('.isotope-container'), function() {
      initIsotope = new Isotope(isotopeItem.querySelector('.isotope-container'), {
        itemSelector: '.isotope-item',
        layoutMode: layout,
        filter: filter,
        sortBy: sort
      });
    });

    isotopeItem.querySelectorAll('.isotope-filters li').forEach(function(filters) {
      filters.addEventListener('click', function() {
        isotopeItem.querySelector('.isotope-filters .filter-active').classList.remove('filter-active');
        this.classList.add('filter-active');
        initIsotope.arrange({
          filter: this.getAttribute('data-filter')
        });
        if (typeof aosInit === 'function') {
          aosInit();
        }
      }, false);
    });

  });

  /**
   * Init swiper sliders
   */
  function initSwiper() {
    document.querySelectorAll(".init-swiper").forEach(function(swiperElement) {
      let config = JSON.parse(
        swiperElement.querySelector(".swiper-config").innerHTML.trim()
      );

      if (swiperElement.classList.contains("swiper-tab")) {
        initSwiperWithCustomPagination(swiperElement, config);
      } else {
        new Swiper(swiperElement, config);
      }
    });
  }

  window.addEventListener("load", initSwiper);

  /**
   * Correct scrolling position upon page load for URLs containing hash links.
   */
  window.addEventListener('load', function(e) {
    if (window.location.hash) {
      if (document.querySelector(window.location.hash)) {
        setTimeout(() => {
          let section = document.querySelector(window.location.hash);
          let scrollMarginTop = getComputedStyle(section).scrollMarginTop;
          window.scrollTo({
            top: section.offsetTop - parseInt(scrollMarginTop),
            behavior: 'smooth'
          });
        }, 100);
      }
    }
  });

  /**
   * Navmenu Scrollspy
   */
  let navmenulinks = document.querySelectorAll('.navmenu a');

  function navmenuScrollspy() {
    navmenulinks.forEach(navmenulink => {
      if (!navmenulink.hash) return;
      let section = document.querySelector(navmenulink.hash);
      if (!section) return;
      let position = window.scrollY + 200;
      if (position >= section.offsetTop && position <= (section.offsetTop + section.offsetHeight)) {
        document.querySelectorAll('.navmenu a.active').forEach(link => link.classList.remove('active'));
        navmenulink.classList.add('active');
      } else {
        navmenulink.classList.remove('active');
      }
    })
  }
  window.addEventListener('load', navmenuScrollspy);
  document.addEventListener('scroll', navmenuScrollspy);


  /**
   * Contact Form Logic
   */
  document.addEventListener('DOMContentLoaded', () => {
    let contactForm = document.querySelector('.php-email-form'); // This is the form with class .php-email-form

    if (contactForm) {
      contactForm.addEventListener('submit', (e) => {
        e.preventDefault(); // Prevent default form submission

        let thisForm = e.target;
        let formData = new FormData(thisForm);

        let loadingDiv = thisForm.querySelector('.loading');
        let errorMessageDiv = thisForm.querySelector('.error-message');
        let sentMessageDiv = thisForm.querySelector('.sent-message');

        // 1. Show loading message and hide others
        if (loadingDiv) {
            loadingDiv.classList.add('d-block');
            loadingDiv.classList.remove('d-none'); // Ensure loading is visible
        }
        if (errorMessageDiv) {
            errorMessageDiv.classList.remove('d-block');
            errorMessageDiv.classList.add('d-none'); // Ensure error is hidden
            errorMessageDiv.innerHTML = ''; // Clear previous error
        }
        if (sentMessageDiv) {
            sentMessageDiv.classList.remove('d-block');
            sentMessageDiv.classList.add('d-none'); // Ensure success is hidden
            sentMessageDiv.innerHTML = ''; // Clear previous success message
        }

        let xhr = new XMLHttpRequest();
        xhr.open('POST', '/send_email', true); // Flask endpoint

        xhr.onload = () => {
          // 2. Hide loading message once response is received
          if (loadingDiv) loadingDiv.classList.remove('d-block');

          let response;
          try {
            response = JSON.parse(xhr.responseText); // Parse the JSON response from Flask
          } catch (e) {
            // Handle cases where Flask doesn't return valid JSON (e.g., server crash)
            console.error('Error parsing JSON response from server:', e, xhr.responseText);
            if (errorMessageDiv) {
                errorMessageDiv.classList.add('d-block');
                errorMessageDiv.innerHTML = 'An unexpected error occurred. Please try again.';
            }
            return; // Stop execution here
          }

          // 3. Display success or error message based on Flask's response
          if (response.status === 'success') {
            if (sentMessageDiv) {
                sentMessageDiv.innerHTML = response.message;
                errorMessageDiv.classList.remove('d-block'); // Ensure error is hidden
                errorMessageDiv.classList.add('d-none'); // Ensure error is hidden if it was ever visible
                sentMessageDiv.classList.remove('d-none'); // <<< REMOVE d-none
                sentMessageDiv.classList.add('d-block'); // <<< ADD d-block
            }
            thisForm.reset(); // Clear form fields on success
          } else {
            // Server returned an error status
            if (errorMessageDiv) {
                errorMessageDiv.innerHTML = response.message;
                sentMessageDiv.classList.remove('d-block'); // Ensure success is hidden
                sentMessageDiv.classList.add('d-none'); // Ensure success is hidden if it was ever visible
                errorMessageDiv.classList.remove('d-none'); // <<< REMOVE d-none
                errorMessageDiv.classList.add('d-block'); // <<< ADD d-block
            }
            console.error("Server reported an error:", response.message);
          }
        };

        xhr.onerror = () => { // Handle network-level errors (e.g., server not running, connection lost)
          if (loadingDiv) loadingDiv.classList.remove('d-block'); // Hide loading
          if (errorMessageDiv) {
              errorMessageDiv.classList.add('d-block');
              errorMessageDiv.innerHTML = "Network error: Could not connect to the server. Please check your connection and try again.";
          }
          if (sentMessageDiv) sentMessageDiv.classList.remove('d-block'); // Ensure success message is hidden
          console.error("Network error during form submission.");
        };

        xhr.send(formData); // Send the form data
      });
    }
  });

})();