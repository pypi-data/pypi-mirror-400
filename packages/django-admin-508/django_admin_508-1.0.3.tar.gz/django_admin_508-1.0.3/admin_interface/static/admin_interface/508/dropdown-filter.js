/** global: django */

if (typeof (django) !== 'undefined' && typeof (django.jQuery) !== 'undefined') {
  (function ($) {
    'use strict';
    $(document).ready(function () {
      const filters = document.querySelectorAll('#changelist-filter .list-filter-dropdown select')
      let query = ''
      // Override the default onchange handler of each filter
      for (const filter of filters) {
        // This needs to be a function expression so `this` references the filter elements themselves
        filter.onchange = function() {
          let value = this.options[this.selectedIndex].value
          if (query !== '') {
          	value = value.replace('?', '&')
	        }
          query = query.concat(value)
        };
      }

      const applyFiltersButton = document.querySelector('#submit-filters');
      if (applyFiltersButton) {
        applyFiltersButton.onclick = function () {
          window.location = query
        };
      }
    });
  })(django.jQuery);
}
