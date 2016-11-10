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

/* globals... */
var data_cache = {};
var charts = {};
console.log(window.location.pathname);
//We strip off the ids and should have a useful app base that will work for any server context
var appbase = window.location.pathname.replace(/\/\d+(|\/)/g, "");
var serverbase = window.location.pathname.replace(/(|\/\w+)\/\d+(|\/)/g, "");

console.log("APPBASE: ",appbase);
console.log("SERVERBASE: ",serverbase);



$(document).ready(function(){
	$("#id_language").on("change keyup", function () {
		$(this).closest("form").submit();
	});
	//actions (always)
	console.log("STATIC_URL: ",static_url);	
	actions_table = init_actions_table();
	init_date_inputs(actions_table);
	init_actions_chart();
	init_user_actions_chart();
	init_top_users_chart();
	init_top_collections_chart()

	init_user_list();

	init_collections_table();
	init_users_table();
	init_documents_table();
//	init_pages_table();
	init_pages_thumbs();

	init_chart_filters();
});
function make_url(url){
	appbase = appbase.replace(/\/$/,""); //remove trailing slash from appbase
	return appbase+url;
}
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
	var url = make_url("/table_ajax/actions");
	console.log("Using appbase: ",url);

//	var url = "./table_ajax/actions";
	var context = '';
	for(x in ids){
		console.log(x," => ",ids[x])
		context += '/'+ids[x];
	};
	url += context;
	console.log("URL: ",url);
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

function init_users_table(){

	if(!$("#users_table").length) return;

	var ids = parse_path();
	var url = make_url("/table_ajax/users");

	var context = '';
	for(x in ids){
		context += '/'+ids[x];
	};
	url += context;
	var columns =  [
		    { "data": "userId", "visible": false  },
		    { "data": "userName"},
		    { "data": "firstname" },
		    { "data": "lastname" },
		    { "data": "email" },
		    { "data": "affiliation" },
		    { "data": "created" },
		    { "data": "role" },
        	];
	return init_datatable($("#users_table"),url,columns);
}
function init_collections_table(){

	if(!$("#collections_table").length) return;

	var url = make_url("/table_ajax/collections");

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

//	var url = "./table_ajax/documents/"+window.location.pathname.replace(/^.*\/(\d+)$/, '$1');
	var url = make_url("/table_ajax/documents/"+window.location.pathname.replace(/^.*\/(\d+)$/, '$1'));

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

//	var url = "./table_ajax/pages"+window.location.pathname.replace(/^.*\/(\d+\/\d+)$/, '$1');
	var url = make_url("/table_ajax/pages"+window.location.pathname.replace(/^.*\/(\d+\/\d+)$/, '$1'));



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

function init_datatable(table,url, columns){
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
		},		
//		"sDom": "rltip",
		"dom": '<"top">rt<"bottom"lip><"clear">',
		"length" : 5,
		"lengthMenu": [ 5, 10, 20, 50, 100 ],
		//ordering should be handled server side
		"ordering": false,  //still not sure about this
		"columns": columns,
		"createdRow": function ( row, data, index ) {
                	$(row).addClass("clickable");
			//make rows click through to wheresoever they have an id for (col,doc,page)
                	$(row).on("click", function(){ 
				//TODO TODO make these linked rows work for user table
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
					url = serverbase+'/edit/correct/'+data.colId+'/'+data.docId+'/'+data.pageNr;
				//TODO add case for userlist links 
				if(url){
					 window.location.href=appbase+'/'+url;
				}
			});
        	},

	});
	$(".table_filter").on("click", function(){
		 datatable.columns( 5 )
        	.search( this.value )
        	.draw();
		return false;
	});
	$(table).on( 'draw.dt', function () {
		$("#"+$(table).attr("id")+"_count").html(datatable.page.info().recordsTotal);
	} );
	return datatable;
}


function init_actions_chart(){

	if(!$("#actions_line").length) return;
	ids=parse_path();
//	var url = static_url+"/dashboard/chart_ajax/actions/line";
	var url = make_url("/chart_ajax/actions/line");

	for(id in ids){
		url += '/'+ids[id];
	}
	init_chart("actions_line",url,"line");

}

//TODO propogate / better integrate this
function init_user_actions_chart(userid,canvas_id){

	if(canvas_id == undefined) canvas_id = "user_actions_line";
	if(!$("#"+canvas_id).length) return;
	ids=parse_path();
	//userid is set in header template and is the current_userid of currently logged in user
//	console.log("USERNAME: ",current_userid);
	if(userid == undefined) userid = current_userid;
//	var url = static_url+"/dashboard/chart_ajax/u/"+userid+"/actions/line";
	var url = make_url("/chart_ajax/u/"+userid+"/actions/line");

	for(id in ids){
		url += '/'+ids[id];
	}
	init_chart(canvas_id,url,"line");
}

function init_top_users_chart(){

	if(!$("#top_users").length) return;
	ids=parse_path();
//	var url = static_url+"/dashboard/chart_ajax/actions/top_bar/userId/userName";
	var url = make_url("/chart_ajax/actions/top_bar/userId/userName");

	for(id in ids){
		url += '/'+ids[id];
	}
	init_chart("top_users",url,"bar");
}

function init_top_collections_chart(){

	if(!$("#top_collections").length) return;
	ids=parse_path();
//	var url = static_url+"/dashboard/chart_ajax/actions/top_bar/colId/colName";
	var url = make_url("/chart_ajax/actions/top_bar/colId/colName");

	init_chart("top_collections",url,"bar");
}


function init_user_list(){
	if(!$("#user_list").length) return;
	ids=parse_path();
//	var url = static_url+"/dashboard/table_ajax/users"; //use table data with -1... *nascent* javascript caching... will need to use url+paramss to stop pollution
	var url = make_url("/table_ajax/users"); //use table data with -1... *nascent* javascript caching... will need to use url+paramss to stop pollution

	for(id in ids){
		url += '/'+ids[id];
	}
	init_list("user_list",url);
}

function init_list(list_id,url){
	if(data_cache[url]){ // here we check cache
		make_list(list_id,data_cache[url]);
	}

	$.ajax({
	    'type': 'GET',
    	    'url': url,
	    'data': {length: -1}, //insist on all values...?
            'dataType': 'json',
            'success': function (data) {
		data_cache[url] = data; //cache the cahrt data as it is generally much bigger
		make_list(list_id,data);
 	     },
	});
}	
function make_list(list_id,data){

	$("#"+list_id).html(""); //clearout

	for(i in data.data){
		$("#"+list_id).append('<li data-userid="'+data.data[i].userId+'"><a href="#'+list_id+'_panel" data-toggle="tab">'+data.data[i].userName+'</a></li>');
	}

	$("#"+list_id+" > li").on("click", function(){
		console.log("load user data for...?", this, $("a", this).attr("href"), $(this).data("userid") );
		init_user_actions_chart( $(this).data("userid"),"user_actions_line_x");
	});
}
function init_chart(canvas_id,url,chart_type){
	console.log("url: ",url);
	console.log("ccanvas: ",canvas_id);


	$.ajax({
	    'type': 'GET',
    	    'url': url,
	  //  data: {length: length, start: start},
            'dataType': 'json',
            'success': function (data) {
		data_cache[url] = data; //cache the cahrt data as it is generally much bigger

		if(data.labels.length == 0 && data.datasets.length ==0){
			console.log(data.labels,data.datasets)
			//TODO tigger panel so we can see a message
			$("#"+canvas_id).html("No data available");
		}
		if(chart_type == 'bar')
			Chart.defaults.global.legend.display = false;
		else
			Chart.defaults.global.legend.display = true;

		charts[canvas_id] = new Chart(document.getElementById(canvas_id).getContext('2d'), {
		    type: chart_type,
		    data: data,
/* options: {
        legend: {
            onClick : function(event, legendItem)  { console.log("legend clicked\n")}
        }
    }
*/
 		});


		$("#"+canvas_id).on("click",
		    function(e){
			//where appropriate we can navigate by clicking on chart bar/lines/segmments
			//only tested for collection bars presently
			var chart =  charts[canvas_id];
	        
			activeElement = chart.getElementAtEvent(e);
			if(activeElement[0] == undefined) return; //not clicked on a dataset
			var clicked_value = data.datasets[activeElement[0]._datasetIndex].data[activeElement[0]._index];
			var clicked_label = data.labels[activeElement[0]._index];
			if(data.label_ids == undefined) return; //no label ids avialable for forwarding
			var clicked_id = data.label_ids[activeElement[0]._index];

			var ids = parse_path();
			var url = static_url+"/dashboard";
			var context = '';
			for(x in ids){
				context += '/'+ids[x];
			};
			url += context+'/'+clicked_id;

			console.log("CLICK: ",clicked_id);
			console.log("URL: ",url);
		 	window.location.href=static_url+url;
		    }
		);  

	    }
	});

}	
function init_chart_filters(){

	$(".table_filter").on("click", function(){
		active_canvas = $(".tab-pane.active > canvas").attr("id");
		console.log("table_filter CLICKED",active_canvas);

		if($("#"+active_canvas).length==0) return false;

		var chart =  charts[active_canvas];
		//TODO the hiding needs to be inversed to make click on the button positive (ie just show clicked, rather than hide clicked)
		for(x in chart.data.datasets){
			var a=chart.getDatasetMeta(x);
			a.hidden=null;
		}
		if($(this).attr("id") === "filter_clear"){ chart.update(); return;}

		var n=parseInt($(this).val())-1;
		for(x in chart.data.datasets){
			if(n!=x){
				var a=chart.getDatasetMeta(x);
				a.hidden=null===a.hidden ?! chart.data.datasets[x].hidden : null;
			}

		}
		chart.update();
		return false;

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
//	var url = static_url+"/dashboard/table_ajax/pages/"+ids['collId']+'/'+ids['docId'];
	var url = make_url("/table_ajax/pages/"+ids['collId']+'/'+ids['docId']);


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
			var status_label = data.data[x].status.ucfirst().replace(/_/," ");
			var thumb = $('<div class="col-md-2"><a href="'+serverbase+'/edit/correct/'+ids['collId']+'/'+ids['docId']+'/'+data.data[x].pageNr+'" class="thumbnail '+data.data[x].status+'"><img src="'+data.data[x].thumbUrl+'"><div class="thumb_label">'+status_label+'</div></a></div>');
			$(row).append(thumb);
		}
		$("#pages_thumbnail_grid").html(menu);
		$("#pages_thumbnail_grid").append(row);
		var end = start+length;
		if(end > data.recordsTotal) end = data.recordsTotal;
		$("#pages_thumbnail_grid").append('<div class="dataTables_info" id="pages_thumb_info" data-thumb-total="'+data.recordsTotal+'">Showing '+start+' to '+end+' of '+data.recordsTotal+'</div>');

		if(length<data.recordsTotal){
			paginate("pages_thumbnail_grid",start,length,data.recordsTotal);
		}
           }
	});

}
//emulates the dataTables pagination for things that aren't tables, but need paginated (ie thumbgrids)
function paginate(id,start,length,total){
	var paginate_html = '<div class="dataTables_wrapper"><div class="dataTables_paginate paging_simple_numbers" id="thumb_pagination">'+
	'<a href="previous" id="pages_thumb_previous" class="paginate_button previous">Previous</a>'+
	'<span></span>'+
	'<a href="next" id="pages_thumb_next" class="paginate_button next">Next</a></div></div>';
	var paginate = $(paginate_html);
	var pages = Math.round(total/length)+1;
	var show_page_limit = 5;
	var curr_page = current_page(start,length);
	for(page=1; page<pages; page++){
	//	var curr_page = page*length;
		if(pages > show_page_limit){
			var onwards = true;
			if((page+1) == curr_page) onwards = false;
			if((page-1) == curr_page) onwards = false;
			if(page == curr_page) onwards = false;
			if(curr_page < show_page_limit && page <= show_page_limit) onwards = false;
			if(curr_page > (pages-show_page_limit) && page >= (pages-show_page_limit)) onwards = false;
			if(page == (pages-1)) onwards = false;
			if(page == 1) onwards = false;
			if(onwards) continue;
		}
		var p = $('<a href="'+((page-1)*length)+'" class="paginate_button">'+page+'</a>');

		if(page== (pages-1) && curr_page <= (pages-show_page_limit))
			$("span[class!='elipses']", paginate).append('<span class="elipses">...</span>');
		$("span[class!='elipses']", paginate).append(p);
		if(page== 1 && curr_page >= show_page_limit)
			$("span[class!='elipses']", paginate).append('<span class="elipses">...</span>');

		if(page == curr_page)
			$(p).addClass("current").siblings("a").removeClass("current");

	};
	if(start == 0 ) { $("#pages_thumb_previous",paginate).addClass("disabled"); }
	if(start+length >= total ) { $("#pages_thumb_next",paginate).addClass("disabled"); }

	$("#"+id).append(paginate);

}
function current_page(start,length){
	return Math.floor(start/length)+1;
}

String.prototype.ucfirst = function() {
    return this.charAt(0).toUpperCase() + this.slice(1).toLowerCase();
}

function parse_path(){
	var pattern = /\/dashboard(|\/(\d+)(|\/(\d+)(|\/(\d+))))$/;
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


