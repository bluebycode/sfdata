$body = $("body");

$(document).on({
  //ajaxStart: function() { $body.addClass("loading");    },
  //ajaxStop:  function() { $body.removeClass("loading"); }    
});

var attributes = new Bloodhound({
    datumTokenizer: Bloodhound.tokenizers.obj.whitespace('text'),
    queryTokenizer: Bloodhound.tokenizers.whitespace,
    prefetch: '/data/attributes.json'
});
attributes.clearPrefetchCache();
attributes.initialize();

var elt = $('input[name="tags"]');
elt.tagsinput({
    tagClass: function(item) {
        switch (item.attribute) {
          case 'district'   : return 'label label-primary';
          case 'category'  : return 'label label-danger label-important';
        }
      },
      maxTags: 6,
      itemValue: 'value',
      itemText: 'text',
      typeaheadjs: [{
        hint: true,
        highlight: true,
        minLength: 1
      },{
        name: 'attributes',
        displayKey: 'text',
        source: attributes.ttAdapter()
      }]
});

elt.on('itemAdded', function(event) {
  //console.log(event.item);  
});

$('.bootstrap-tagsinput input').on('keydown', (e) => {
  if (e.keyCode == 9) e.preventDefault()
  if (e.keyCode == 13) {
    e.preventDefault();
    refresh();
  }
});

$('.bootstrap-tagsinput input').on('itemRemoved', (e) => {
  refresh();
});

let getCurrentYear = () => $('button#selectYear').text().trim().substring(0,4)

let getCurrentTags = () => {
  let values = elt.tagsinput('items');
  let tags = {};
  for (const e of values) {
    if (!tags[e.attribute]) tags[e.attribute] = [];
    tags[e.attribute].push(e.text);
  }
  return tags;
}

let ajaxRendersMap = function(json){
  $('#map-frame').attr('src', "generated_map/" + btoa(json));
  $body.addClass("loading");
}

let refresh = () => {
  let tags = getCurrentTags();
  let year = getCurrentYear();
  if (year && year != undefined && year!='2017'){
    tags['year'] = year;
  }
  ajaxRendersMap(JSON.stringify(tags));
}

$('#apply-button').on('click', function(event) {
  event.preventDefault();
  refresh();
});


$('input[name="daterange"]').daterangepicker({
  opens: 'left'
}, function(start, end, label) {
  console.log("A new date selection was made: " + start.format('YYYY-MM-DD') + ' to ' + end.format('YYYY-MM-DD'));
});

$("#map-frame").on("load", function () {
  console.log("Map reloaded!");
  $body.removeClass("loading");
})

$('ul#selectYearSelections li').on('click', (e) => {
  $('button#selectYear').html(e.target.text + '  <span class="caret"></span><span class="sr-only">Toggle Dropdown</span>');
  refresh();
});
  