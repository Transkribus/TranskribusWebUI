function getCookie(cookieName) {
    var cookieArray = document.cookie.split(';');
    for(var i = 0; i < cookieArray.length; i++) {
        var cookie = cookieArray[i];
        while (cookie.charAt(0)==' ') {
            cookie = cookie.substring(1);
        }
        if (cookie.indexOf(cookieName) == 0) {
            return cookie.substring(cookieName.length + 1, cookie.length);
        }
	}
	return "";
}

function jobCountsChanged(json) {
	jobs = getCookie("jobs");
	stringified = JSON.stringify(json);
	if ("" == jobs) {// TODO Decide whether to consider changes in jobs between sessions worth informing the user about. Cookie expiration decides this. 
		document.cookie = "jobs=" + stringified; 
	} else if (jobs != stringified) {
		document.cookie = "jobs=" + stringified;
		document.cookie = "changes_acknowledged=false";
		jobStatusAlert();
	} else {
			$('.changed-jobs-content').load(jobs_list_compact);// Refresh the modal if job statuses have changed since it was shown.
	}
}

function jobCountsPoll() { 
	setTimeout(function(){
			$.ajax({ url: job_count_url, method: 'GET', success: function(json) {
			jobCountsChanged(json);
			jobCountsPoll();
		}});
	}, 5000);// How frequent?
}

function jobStatusAlert() {
	if("" == $('.changed-jobs-modal').html()) {// Are we already showing the modal?
		$('.changed-jobs-modal').load(changed_jobs_modal);// No, prepare it.
		$('.job-notification').show();// Note: It's unnecessary to show this when the modal is shown so we don't do it below.
	} else {
		$('.changed-jobs-content').load(jobs_list_compact);// Refresh the modal if job statuses have changed since it was shown.
	}	
}

$(document).ready(function(){
	$(".menu-toggle-wrapper").css("height",window.innerHeight+'px');
});			

window.onload = function() {
	if (getCookie("changes_acknowledged") == "false") // We show this on every page until the user acknowledges the changes by clicking away the alert.
		jobStatusAlert();
		jobCountsPoll();
	$(".job-notification-close").click(function(event) {
		document.cookie = "changes_acknowledged=true";
		$('.job-notification').hide();
	});
}
