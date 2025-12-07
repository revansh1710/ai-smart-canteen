console.log("AI Smart Canteen JS loaded");

// Example: simple form validation
document.addEventListener("DOMContentLoaded", function() {
    const forms = document.querySelectorAll("form");
    forms.forEach(form => {
        form.addEventListener("submit", function(e){
            const inputs = form.querySelectorAll("input");
            for(let i=0;i<inputs.length;i++){
                if(inputs[i].value.trim() === ""){
                    e.preventDefault();
                    alert("Please fill all fields!");
                    return;
                }
            }
        });
    });
});
