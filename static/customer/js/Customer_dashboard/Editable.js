function UserDetails()
{
    document.getElementById("first-name").disabled = false;
    document.getElementById("last-name").disabled = false;
    document.getElementById("father_name").disabled = false;
    document.getElementById("gender").disabled = false;
    document.getElementById("dob").disabled = false;
    document.getElementById("state").disabled = false;
    document.getElementById("city").disabled = false;
    document.getElementById("current-add").disabled = false;
    document.getElementById("postal").disabled = false;
    document.getElementById("email").disabled = false;
    document.getElementById("mobile").disabled = false;
    document.getElementById("bank-name").disabled = false;
    document.getElementById("account").disabled = false;
    document.getElementById("branch").disabled = false;
    document.getElementById("ifsc").disabled = false;
    document.getElementById("account-holder").disabled = false;
    document.getElementById("nominee-name").disabled = false;
    document.getElementById("relation").disabled = false;
    document.getElementById("nominee-dob").disabled = false;
}

function selectedvalue() {
    var e = document.getElementById("scheme");
    var strUser = e.options[e.selectedIndex].value;
    if(strUser == 0)
    {
           document.getElementById("Non-Breakable").style.display="block";
           document.getElementById("Breakable").style.display="none";

    }
    else if(strUser == 1)
    {
        document.getElementById("Breakable").style.display="block";
        document.getElementById("Non-Breakable").style.display="none";
    }
    else{
          document.getElementById("Non-Breakable").style.display="none";
          document.getElementById("Breakable").style.display="none";
    }
}

function non_ROI() {
    var e = document.getElementById("scheme");
    var strUser = e.options[e.selectedIndex].value;
    if(strUser == 0)
    {
           document.getElementById("Non-Breakable").style.display="block";
           document.getElementById("Breakable").style.display="none";
    }
    else if(strUser == 1)
    {
        document.getElementById("Breakable").style.display="block";
        document.getElementById("Non-Breakable").style.display="none";
    }
    else{
          document.getElementById("Non-Breakable").style.display="none";
          document.getElementById("Breakable").style.display="none";
    }
}






