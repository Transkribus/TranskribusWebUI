
$(document).ready(function(){
	$(".menu-toggle-wrapper").css("height",window.innerHeight+'px');
});

/* Collections */

glyph_opts = {
    map: {
      doc: "glyphicon glyphicon-file",
      docOpen: "glyphicon glyphicon-file",
      checkbox: "glyphicon glyphicon-unchecked",
      checkboxSelected: "glyphicon glyphicon-check",
      checkboxUnknown: "glyphicon glyphicon-share",
      dragHelper: "glyphicon glyphicon-play",
      dropMarker: "glyphicon glyphicon-arrow-right",
      error: "glyphicon glyphicon-warning-sign",
      expanderClosed: "glyphicon glyphicon-plus-sign",
      expanderLazy: "glyphicon glyphicon-plus-sign",  // glyphicon-expand
      expanderOpen: "glyphicon glyphicon-minus-sign",  // glyphicon-collapse-down
      folder: "glyphicon glyphicon-folder-close",
      folderOpen: "glyphicon glyphicon-folder-open",
      loading: "glyphicon glyphicon-refresh"
    }
  };

$(document).ready(function(){

    	$(".menu-toggle").click(function(e) {

	   if($(this).attr("id") === "menu-toggle-in"){
		$(".read_nav_out").show();
		$(".read_nav_in").hide();
		localStorage.setItem("sidebar_state", "in");
	   }else{
		$(".read_nav_out").hide();
		$(".read_nav_in").show();
		localStorage.setItem("sidebar_state", "out");
	   }
           $("#wrapper").toggleClass("toggled");
           e.preventDefault();

    	});

   	$("#collections_tree").fancytree({
	  source: t_data,  //source in from transkribus
/*
 * Minimal structure for fancytree rendering
 * [
	    {title: "Collection", key: "1", folder: true, children: [
		      {title: "Document", key: "1.1"},
		      {title: "Document", key: "1.2"}	
	    ]},
	    {title: "Collection", key: "2", folder: true, children: [
	      {title: "Document", key: "2.1"},
	      {title: "Document", key: "2.2"}
	    ]}
	  ],
*/
 	  extensions: ["glyph", "wide"],
	  glyph: glyph_opts,
	  checkbox: true,
	  selectMode: 2,
	  loadChildren: function(event, data) {
		console.log("Loaded children...",data);
      	  },
	  activate: function(event, data){
            	var node = data.node,
                orgEvent = data.originalEvent;
		console.log("active node: ",data);

           },
	});

	$(".panel-expand").click(function(){
		var button = this;
//		$(this).parents(".expandable").removeClass("col-md-4", function(){
	
		var class_to_remove = ($(this).parents(".expandable").attr("class").match(/(^|\s)col-md-\S+/g) || []).join(' ');
		$(this).parents(".expandable").removeClass(class_to_remove, function(){

			$(this).addClass("col-md-12");
			$(button).hide(function(){
				$(button).siblings(".panel-shrink").attr("data-return-class",class_to_remove);
				$(button).siblings(".panel-shrink").show()
			});

		});
	});
	$(".panel-shrink").click(function(){
		var button = this;
		var class_to_reinstate = $(button).attr("data-return-class");
		$(this).parents(".expandable").addClass(class_to_reinstate, function(){
			$(this).removeClass("col-md-12");
			$(button).hide(function(){$(button).siblings(".panel-expand").show()});
		});
	});

});
