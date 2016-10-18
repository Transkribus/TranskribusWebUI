$(document).ready(function(){
	$(".menu-toggle-wrapper").css("height",window.innerHeight+'px');

	var sidebar_state = localStorage.getItem("sidebar_state");
	if (sidebar_state === "in") {
		$("#wrapper").toggleClass("toggled");
		$(".read_nav_out").show();
		$(".read_nav_in").hide();
	} else {
		$(".read_nav_in").show();
		$(".read_nav_out").hide();
	}
});


$(document).ready(function(){
	$("#id_language").on("change keyup", function () {
		$(this).closest("form").submit();
	});
	//actions (always)
	actions_table = init_actions_table();
	init_date_inputs(actions_table);
	//dashboard only
	init_collections_table();
	//dashboard/{colId} only
	init_documents_table();

});

function init_date_inputs(actions_table){

    var min = new Date('2016.01.01').getTime() / 1000;
    var max = new Date().getTime() / 1000;

    var slider = $( "#slider-range" ).slider({
      range: true,
      min: min, //seconds
      max: max,
      step: 86400,
      values: [ min, max ],
      slide: function( event, ui ) {
        $( "#start_date" ).val( (new Date(ui.values[ 0 ] *1000).toDateString() ) );
        $( "#end_date" ).val( (new Date(ui.values[ 1 ] *1000)).toDateString() );
      },
      change: function(event, ui){
	//if the slider values change we reload the data table...
	actions_table.ajax.reload();
      }
    });
    $( "#start_date" ).datepicker({"dateFormat":"D M dd yy", "onSelect": function(date){
		console.log("start date picker onSelect");
		slide_end = slider.slider("option", "values")[1];
		slider.slider( "option", "values", [($(this).datepicker("getDate")/1000),slide_end] );
	}}).val(new Date(min*1000).toDateString());
    $( "#end_date" ).datepicker({"dateFormat":"D M dd yy","onSelect": function(date){
		console.log("end date picker onSelect");
		slide_start = slider.slider("option", "values")[0];
		slider.slider( "option", "values", [slide_start,($(this).datepicker("getDate")/1000)] );
	}}).val(new Date(max*1000).toDateString());

}
function init_actions_table(){
	var url = "/dashboard/actions_for_table_ajax";
	if($("#actions_table").attr("data-collid")){
		url += "/"+$("#actions_table").data("collid");
	}
	var columns =  [
		    { "data": "time" },
		    { "data": "colId" },
		    { "data": "docId" },
		    { "data": "pageId" },
		    { "data": "userName" },
		    { "data": "type" }
        	];
	return init_datatable($("#actions_table"),url,columns);
}
function init_collections_table(){
	var url = "/dashboard/collections_for_table_ajax";
	var columns =  [
		    { "data": "colId" },
		    { "data": "colName" },
		    { "data": "description" },
		    { "data": "role" },
        	];
	init_datatable($("#collections_table"),url,columns,"colName","colId");
}

function init_documents_table(){
	var url = "/dashboard/documents_for_table_ajax/"+window.location.pathname.replace(/^.*\/(\d+)$/, '$1');
	var columns =  [
		    { "data": "docId" },
		    { "data": "title" },
		    { "data": "author" },
		    { "data": "uploadTimestamp" },
		    { "data": "uploader" },
		    { "data": "nrOfPages" },
		    { "data": "language" },
		    { "data": "status" },
        	];
	init_datatable($("#documents_table"),url,columns,"title","docId");
}

function init_datatable(table,url, columns,id_link,id_field){
	var datatable = table.DataTable({
		"processing": true,
        	"serverSide": true,
		"ajax": {
			"url": url,
			"data": function ( d ) {
				if($("#slider-range").data("uiSlider")){
					return $.extend( {}, d, { 
						"start_date": ($("#slider-range").slider("option", "values")[0]*1000),
						"end_date":($("#slider-range").slider("option", "values")[1]*1000) ,
					});
				}
			},
			"error": function (xhr, error, thrown) {
				//for now we assume that a problem with the ajax request means 
				//that TS REST session is expired and you need logged out... 
				//this could be annoying if not the case though!
				//TODO needs query string too...?
				alert("There was an issue communicating with the transkribus service Please try again, if the problem persists send the error below to....\n ",error, thrown);
//				window.location.replace("/login/?next="+window.location.pathname)
			},
			"dataSrc": function ( json ) {
				if(id_link == undefined || id_field == undefined) return json.data;
				
				var ids = parse_path();	
			      for ( var i=0, ien=json.data.length ; i<ien ; i++ ) {
				link_str = '/dashboard';
				for(x in ids){
					link_str += '/'+ids[x];
				}
				link_str += '/'+json.data[i][id_field];

 				json.data[i][id_link] = '<a href="'+link_str+'">'+json.data[i][id_link]+'</a>';

				console.log(json.data[i][id_link]);
			      }
			      return json.data;
			},
		},		
		"sDom": "rltip",
		"length" : 5,
		"lengthMenu": [ 5, 10, 20, 50, 100 ],
		//ordering should be handled server side
		"ordering": false,  //still not sure about this
		"columns": columns,
	});
	$(".table_filter").on("click", function(){
		 datatable.columns( 5 )
        	.search( this.value )
        	.draw();
		return false;
	});
	return datatable;
}

function parse_path(){
	var pattern = /^\/dashboard\/(\d+)(|\/(\d+)(|\/(\d+)))$/;
	var result = pattern.exec(window.location.pathname);
	ids = {};
	if(result != null && result[1]) ids['collId'] = result[1];
	if(result != null && result[2]) ids['docId'] = result[2];
	if(result != null && result[3]) ids['pageId'] = result[3];

	return ids;
}
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
/* The fancytree rendering */
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
	if(typeof t_data === "undefined") t_data = [];
//	$(".pager").hide();
	$("#collections_tree").fancytree({
		  source: t_data,  //source in from transkribus
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
			$(".pager").show();
			$(".documents_intro").hide();
			if(node.isFolder()){ //we have a document
				//put the page thumbs back to small
				$(".page_thumb").show().removeClass("col-md-12").addClass("col-md-3");
				//hide other documents	
				$("#doc_"+node.data.docId).siblings(".document_thumbs").hide();
				//show active document
				$("#doc_"+node.data.docId).show().find("span.page_title").html("");

			}else{ //we have a page
				//first show the doc div that this page is in
				$("#page_"+node.key).parents(".document_thumbs").siblings().hide();
				$("#page_"+node.key).parents(".document_thumbs").show();

				//hide all the other pages
				$("#page_"+node.key).siblings(".page_thumb").hide();
				//show active page and make it full size (of panel)
				$("#page_"+node.key).show().removeClass("col-md-3", function(){
					$(this).addClass("col-md-12");
				});

				//update the page_title span in the document h4
				var page_link = "/library/page/"+node.data.collId+"/"+node.data.docId+"/"+node.data.pageNr;

				$("#page_"+node.key).parents(".document_thumbs").find("span.page_title > a").html(node.title).attr("href",page_link);
			}
		   },
	}); //endof fancytree

	/*panel expand/shrink (possibly not used*/
	$(".panel-expand").click(function(){
		var button = this;
//		$(this).parents(".expandable").removeClass("col-md-4", function(){
	
		var class_to_remove = ($(this).parents(".expandable").attr("class").match(/(^|\s)col-md-\S+/g) || []).join(" ");
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


