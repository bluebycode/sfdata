$(document).ready(function(){

    $('.bootstrap-tagsinput input').on('keydown', function(e){ if (e.keyCode == 9)  e.preventDefault() });

    var attributes = new Bloodhound({
        datumTokenizer: Bloodhound.tokenizers.obj.whitespace('text'),
        queryTokenizer: Bloodhound.tokenizers.whitespace,
        prefetch: 'data/attributes.json'
      });
      attributes.initialize();
      
      $('#category').tagsinput({
        tagClass: function(item) {
          switch (item.attribute) {
            case 'District'   : return 'label label-primary';
            case 'Incident'  : return 'label label-danger label-important';
          }
        },
        itemValue: 'value',
        itemText: 'text',
        typeaheadjs: {
          name: 'attributes',
          displayKey: 'text',
          source: attributes.ttAdapter()
        }
      });

/*
    var data = ["Amsterdam",
    "London",
    "Paris",
    "Washington",
    "New York",
    "New Jersey",
    "New Orleans",
    "Los Angeles",
    "Sydney",
    "Melbourne",
    "Canberra",
    "Beijing",
    "New Delhi",
    "Kathmandu",
    "Cairo",
    "Cape Town",
    "Kinshasa"];
var citynames = new Bloodhound({
    datumTokenizer: Bloodhound.tokenizers.obj.whitespace('name'),
    queryTokenizer: Bloodhound.tokenizers.whitespace,
    local: $.map(data, function (city) {
        return {
            name: city
        };
    })
});
citynames.initialize();

    $('#category').tagsinput({
    typeaheadjs: [{
          minLength: 1,
          highlight: true,
    },{
        minlength: 1,
        name: 'citynames',
        displayKey: 'name',
        valueKey: 'name',
        source: citynames.ttAdapter()
    }],
    freeInput: true
});
*/
    /*var districts = new Bloodhound({
        datumTokenizer: Bloodhound.tokenizers.obj.whitespace('name'),
        queryTokenizer: Bloodhound.tokenizers.whitespace,
        prefetch: {
          url: '/districts.json',
          filter: function(list) {
            console.log(list);
            return $.map(list, function(name) {
                console.log(name);
              return { name: name }; });
          }
        }
      });
      districts.initialize();
  
      $('#tags-input').tagsinput({
        typeaheadjs: {
          name: 'districts',
          displayKey: 'name',
          valueKey: 'name',
          source: districts.ttAdapter()
        }
      });*/
});
