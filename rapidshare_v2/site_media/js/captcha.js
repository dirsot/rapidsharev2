var body = document.getElementsByTagName("body")[0];
//body.addEventListener("load", showRecaptcha, false);

function validateCaptcha()
{
	challengeField = $("input#recaptcha_challenge_field").val();
	responseField = $("input#recaptcha_response_field").val();
	//console.log(challengeField);
	//console.log(responseField);
	//return false;
	var html = $.ajax({
		type: "POST",
		url: "http://www.google.com/recaptcha/api/verify",
		data: "recaptcha_challenge_field=" + challengeField + "&recaptcha_response_field=" + responseField,
		async: false
		}).responseText;

	//console.log( html );
	if(html == "success") {
		//Add the Action to the Form
		$("form").attr("action", "http://action/to/the/form_handler");
		//Indicate a Successful Captcha
		$("#captchaStatus").html("Success!");
		// Uncomment the following line in your application
		return true;
	} else {
		$("#captchaStatus").html("The security code you entered did not match. Please try again.");
		Recaptcha.reload();
		return false;
	}
}
function showRecaptcha() 
{
	Recaptcha.create("6LfeH9kSAAAAAB9F4Kdj_t2zzGMVkgprD3nI8HOE", 'captchadiv', {
              
    tabindex: 1,
		theme: "green",
			callback: Recaptcha.focus_response_field
        });
}