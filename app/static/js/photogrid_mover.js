$(document).ready(function(){
    $(function() {
        $( "#sortable" ).sortable({
            update: function(event, ui) {
                console.log(event);
                console.log(ui);
                console.log(ui.position);
            }
        });
        $( "#sortable" ).disableSelection();
    });
});
