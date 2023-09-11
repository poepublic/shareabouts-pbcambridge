
// Toggle between place-specific and city-wide mode
Shareabouts.PlaceFormView.prototype.events['change input[name="city_wide"]'] = 'onCityWideChange';
Shareabouts.PlaceFormView.prototype.onCityWideChange = function(evt) {
  if (evt.currentTarget.checked) {
    this.resetCityWide(evt.currentTarget.value);
  }
}

// Toggle the personal information survey
Shareabouts.PlaceFormView.prototype.events['change input[name="private-completed_personal_info_survey"]'] = 'onPersonalInfoCompleteChange';
Shareabouts.PlaceFormView.prototype.onPersonalInfoCompleteChange = function(evt) {
  if (evt.currentTarget.checked) {
    this.resetPersonalInformationSurvey(evt.currentTarget.value);
  }
}

var original_PlaceFormView_setLatLng = Shareabouts.PlaceFormView.prototype.setLatLng;
Shareabouts.PlaceFormView.prototype.setLatLng = function(ll) {
  original_PlaceFormView_setLatLng.call(this, ll);
  this.$('.approx-address').removeClass('is-visuallyhidden');
}

Shareabouts.PlaceFormView.prototype.unsetLatLng = function() {
  this.center = null;
  this.$('.drag-marker-instructions').removeClass('is-visuallyhidden');
  this.$('.approx-address, .drag-marker-warning').addClass('is-visuallyhidden');
}

Shareabouts.PlaceFormView.prototype.resetCityWide = function(isCityWide) {
  $('body').attr('data-city_wide', isCityWide);

  if (isCityWide == 'true') {
    this.setLatLng({lng: -71.10568553209306, lat: 42.36710953619132}) // <- Cambridge City Hall.
  } else {
    this.unsetLatLng();
  }
}

Shareabouts.PlaceFormView.prototype.initializeGenderField = function() {
  const $radioButtons = this.$('[name="private-gender"][type="radio"]');
  const $selectBoxes = this.$('select[name="private-gender"], select[name="private-gender-alignment"]');

  $radioButtons.on('change', () => {
    $selectBoxes.val('');
  });

  $selectBoxes.on('change', () => {
    $radioButtons.prop('checked', false);
  });
}

Shareabouts.PlaceFormView.prototype.resetPersonalInformationSurvey = function(hasCompleted) {
  // By default, use the personal info completed value from the selected radio
  // button.
  if (hasCompleted === undefined) {
    hasCompleted = this.$('[name="private-completed_personal_info_survey"]:checked').val();
  }

  // If still no value (i.e., no radio button selected), skip setting the attr
  // on the body.
  if (hasCompleted !== undefined) {
    $('body').attr('data-personal-info-complete', hasCompleted);
  }

  if (this.$requiredPersonalInfoFieldCache) {
    this.$requiredPersonalInfoFieldCache.attr('required', 'required');
    this.$requiredPersonalInfoFieldCache = null;
  }

  if (hasCompleted == 'true') {
    this.$requiredPersonalInfoFieldCache = this.$('[data-personal-info][required]')
    this.$requiredPersonalInfoFieldCache.removeAttr('required');
  }
}

var original_PlaceFormView_render = Shareabouts.PlaceFormView.prototype.render;
Shareabouts.PlaceFormView.prototype.render = function() {
  var retVal = original_PlaceFormView_render.call(this);
  this.resetPersonalInformationSurvey();
  this.initializeGenderField();
  return retVal
}

var original_AppView_newPlace = Shareabouts.AppView.prototype.newPlace;
Shareabouts.AppView.prototype.newPlace = function() {
  $('body').removeAttr('data-city_wide');
  $('body').removeAttr('data-personal-info-complete');
  original_AppView_newPlace.call(this);
}