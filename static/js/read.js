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
	init_actions_chart();
	
	init_collections_table();
	init_documents_table();
//	init_pages_table();
	init_pages_thumbs();

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

	if(!$("#actions_table").length) return;

	var ids = parse_path();
	var url = "/dashboard/table_ajax/actions";
	var context = '';
	for(x in ids){
		console.log(x," => ",ids[x])
		context += '/'+ids[x];
	};
	url += context;
	var columns =  [
		    { "data": "time" },
		    { "data": "colId", "visible": false },
		    { "data": "colName" },
		    { "data": "docId", "visible": false  },
		    { "data": "docName" },
		    { "data": "pageId", "visible": false  },
		    { "data": "pageNr" },
		    { "data": "userName" },
		    { "data": "type" }
        	];
	return init_datatable($("#actions_table"),url,columns);
}
function init_collections_table(){

	if(!$("#collections_table").length) return;

//	var url = "/dashboard/collections_for_table_ajax";
	var url = "/dashboard/table_ajax/collections";

	var columns =  [
		    { "data": "colId" },
		    { "data": "colName",
		      "render" : function(data, type, row){
				return '<a href="'+row.colId+'">'+data+'</a>';
			} 
		    },
		    { "data": "description" },
		    { "data": "role" },
        	];
	init_datatable($("#collections_table"),url,columns);
}

function init_documents_table(){

	if(!$("#documents_table").length) return;

//	var url = "/dashboard/documents_for_table_ajax/"+window.location.pathname.replace(/^.*\/(\d+)$/, '$1');
	var url = "/dashboard/table_ajax/documents/"+window.location.pathname.replace(/^.*\/(\d+)$/, '$1');

	var ids = parse_path();	

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
	init_datatable($("#documents_table"),url,columns);
}

function init_pages_table(){

//	var url = "/dashboard/pages_for_table_ajax/"+window.location.pathname.replace(/^.*\/(\d+\/\d+)$/, '$1');
	var url = "/dashboard/table_ajax/pages"+window.location.pathname.replace(/^.*\/(\d+\/\d+)$/, '$1');

	var ids = parse_path();	

	var columns =  [
		    { "data": "pageId" },
		    { "data": "pageNr" },
		    { "data": "thumbUrl" },
		    { "data": "status" },
		    { "data": "nrOfTranscripts" },
        	];
	init_datatable($("#pages_table"),url,columns);

}

function init_actions_chart(){

	if(!$("#actions_line").length) return;
	ids=parse_path();
	var url = "/dashboard/actions_for_chart_ajax";
	for(id in ids){
		url += '/'+ids[id];
	}
	init_chart("actions_line",url);

}

function init_chart(canvas_id,url){
	console.log("url: ",url);

	$.ajax({
	    type: 'GET',
    	    url: url,
	  //  data: {length: length, start: start},
            dataType: 'json',
            success: function (data) {
		chart = new Chart(document.getElementById(canvas_id).getContext('2d'), {
		    type: 'line',
		    data: data,
 		    options: {
			legend: {
			    position : 'bottom'
			},
		   }
		});

	    }
	});
}	
function init_pages_thumbs(){
	// NB This paging is managed on django until we can do so on transkribus rest
	// would be great to manage page size and pages with datatable... but this is not a datatable....
	if(!$("#pages_thumbnail_grid").length) return;

	var start = 0;
	var length = 12;
	get_thumbs(start,length);
	
	$("body").on("change","select[name='pages_thumb_length']",function(){
		var start = parseInt($("#thumb_pagination .paginate_button.current").attr("href"));
		var length = parseInt($(this).val());
		if(length >= parseInt($("#pages_thumb_info").data("thumb-total"))) start = 0;
		get_thumbs(start,length);
	});
	$("body").on("click",".paginate_button",function(){
		if($(this).hasClass("disabled")) return false;
		
		var start = parseInt($(this).attr("href"));
		var length = parseInt($("select[name='pages_thumb_length']").val())
		if($(this).attr("href") === "previous"){ 
			start = parseInt($("#thumb_pagination .paginate_button.current").attr("href"))-length; 
		}
		if($(this).attr("href") === "next"){ 
			start = parseInt($("#thumb_pagination .paginate_button.current").attr("href"))+length; 
		}

		get_thumbs(start,length);
		return false;
	});

}
function get_thumbs(start,length){
//	var url = "/dashboard/thumbnails_ajax/"+window.location.pathname.replace(/^.*\/(\d+\/\d+)$/, '$1');
	var ids = parse_path();	
	var url = "/dashboard/table_ajax/pages/"+ids['collId']+'/'+ids['docId'];

	$.ajax({
	    type: 'GET',
    	    url: url,
	    data: {length: length, start: start},
            dataType: 'json',
            success: function (data) {
		//console.log(data);	
		length_menu = [ 12, 24, 48, 96 ];
		var menu = $('<div><label>Show <select name="pages_thumb_length"></select></label></div>');

		for(i in length_menu){
			var option=$('<option value="'+length_menu[i]+'">'+length_menu[i]+'</option>');
			if(length == length_menu[i]) $(option).attr("selected","selected");
			$("select[name='pages_thumb_length']", menu).append(option);
		}
		var row_html = '<div class="row"></div>';
		var row = $(row_html);
		for(x in data.data){
			var thumb = $('<div class="col-md-2"><a href="/edit/correct/'+ids['collId']+'/'+ids['docId']+'/'+data.data[x].pageNr+'" class="thumbnail"><img src="'+data.data[x].thumbUrl+'"></a></div>');
			$(row).append(thumb);
		}
		$("#pages_thumbnail_grid").html(menu);
		$("#pages_thumbnail_grid").append(row);
		var end = start+length;
		if(end > data.recordsTotal) end = data.recordsTotal;
		$("#pages_thumbnail_grid").append('<div class="dataTables_info" id="pages_thumb_info" data-thumb-total="'+data.recordsTotal+'">Showing '+start+' to '+end+' of '+data.recordsTotal+'</div>');

		if(length<data.recordsTotal){
			var paginate_html = '<div class="dataTables_wrapper"><div class="dataTables_paginate paging_simple_numbers" id="thumb_pagination">'+
			'<a href="previous" id="pages_thumb_previous" class="paginate_button previous">Previous</a>'+
			'<span></span>'+
			'<a href="next" id="pages_thumb_next" class="paginate_button next">Next</a></div></div>';
			var paginate = $(paginate_html);
			var pages = Math.round(data.recordsTotal/length)+1;
			var show_page_limit = 5;
			for(page=1; page<pages; page++){
				var curr_page = page*length;
				if(pages > show_page_limit){
					var onwards = true;
					if(is_current((page+1),start,length)) onwards = false;
					if(is_current((page-1),start,length)) onwards = false;
					if(is_current(page,start,length)) onwards = false;
					if(is_current(page) && page < show_page_limit) onwards = false;
					if(is_current(page) && page > (pages-show_page_limit)) onwards = false;
					if(onwards) continue;
					//if(page > show_page_limit && page != (pages-1)) continue;
				}
				var p = $('<a href="'+((page-1)*length)+'" class="paginate_button">'+page+'</a>');
				if(pages > show_page_limit && page == (pages-1)) 
					p = $('<span> ... <a href="'+((page-1)*length)+'" class="paginate_button">'+page+'</a></span>');

				$("span", paginate).append(p);
				if((page*length) > start && (page*length) < (start+length)+1 ) { $(p).addClass("current").siblings("a").removeClass("current");}
				if(is_current(page,start,length))
					$(p).addClass("current").siblings("a").removeClass("current");

			};
			if(start == 0 ) { $("#pages_thumb_previous",paginate).addClass("disabled"); }
			if(start+length >= data.recordsTotal ) { $("#pages_thumb_next",paginate).addClass("disabled"); }

			$("#pages_thumbnail_grid").append(paginate);
		}
           }
	});

}
function is_current(page,start,length){
	if((page*length) > start && (page*length) < (start+length)+1)
		return true;
	return false;
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
/*
			"dataSrc": function ( json ) {
				//DONE probably better suited in a per column render function
				if(id_link == undefined || id_field == undefined) return json.data;
				
				var ids = parse_path();	
				var ids_len = $.map(ids, function(n, i) { return i; }).length;
			      for ( var i=0, len=json.data.length ; i<len ; i++ ) {

				if(ids_len>1){//page level
					link_str = '/edit/correct';
				}else{
					link_str = '/dashboard';
				}
				for(x in ids){
					link_str += '/'+ids[x];
				}
				link_str += '/'+json.data[i][id_field];

 				json.data[i][id_link] = '<a href="'+link_str+'">'+json.data[i][id_link]+'</a>';

				console.log(json.data[i][id_link]);
			      }
			      return json.data;
			},
*/
		},		
		"sDom": "rltip",
		"length" : 5,
		"lengthMenu": [ 5, 10, 20, 50, 100 ],
		//ordering should be handled server side
		"ordering": false,  //still not sure about this
		"columns": columns,
		"createdRow": function ( row, data, index ) {
                	$(row).addClass("clickable");
			//make rows click through to wheresoever they have an id for (col,doc,page)
                	$(row).on("click", function(){ 
				//TODO this works but feels messy (need to shift that n/a crap from the data for one)
				var ids = parse_path();	
				var colId = null;
				var url = null;
				if(data.colId != undefined && data.colId !== "n/a")
					colId = data.colId;
				if(ids.collId != undefined && ids.collId)
					colId = ids.collId;

				if(colId) url = colId;
				if(data.docId != undefined && data.docId !== "n/a")
					url += '/'+data.docId;
				if(data.pageNr != undefined && data.pageNr !== "n/a") //NB will break until we use base url
					url = '/edit/correct/'+data.colId+'/'+data.docId+'/'+data.pageNr;
				if(url) window.location.href=url;
			});
        	},
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
	var pattern = /^\/dashboard(|\/(\d+)(|\/(\d+)(|\/(\d+))))$/;
	var result = pattern.exec(window.location.pathname);
	ids = {};
	if(result != null && result[2]) ids['collId'] = result[2];
	if(result != null && result[4]) ids['docId'] = result[4];
	if(result != null && result[6]) ids['pageId'] = result[6];

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


