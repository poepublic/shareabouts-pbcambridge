Shareabouts.PlaceFormView.prototype.events['change input[name="private-subscribe"]'] = 'onMailinglistSubscribeChange';
Shareabouts.PlaceFormView.prototype.onMailinglistSubscribeChange = function(evt) {
  var $emailInput = this.$el.find('input[name="private-email"]');
  var $emailOptionalLabel = this.$el.find('label[for="place-private-email"]');

  var labelText = $emailOptionalLabel.text();
  if (evt.target.checked) {
    $emailInput.prop('required', true);
    $emailOptionalLabel.text(labelText.replace('optional', 'required'));
  } else {
    $emailInput.prop('required', false);
    $emailOptionalLabel.text(labelText.replace('required', 'optional'));
  }
};

var mailinglist_original_AppView_viewNewPlace = Shareabouts.AppView.prototype.viewNewPlace;
Shareabouts.AppView.prototype.viewNewPlace = function() {
  mailinglist_original_AppView_viewNewPlace.call(this, ...arguments);
// var original_PlaceFormView_onSaveSuccess = Shareabouts.PlaceFormView.prototype.onSaveSuccess;
// Shareabouts.PlaceFormView.prototype.onSaveSuccess = function(model) {
//   original_PlaceFormView_onSaveSuccess.apply(this, arguments);
  if (this.placeFormView && this.placeFormView.model.get('private-subscribe') === 'true') {
    $.ajax({
      url: '/mailinglist/subscribe',
      type: 'POST',
      data: {
        email: this.placeFormView.model.get('private-email'),
      }
    });
  }
}
