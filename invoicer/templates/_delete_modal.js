<script>
    $( document ).ready(function() {

        // Make sure the user *really* wants to delete the invoice
        $( "#validate_delete" ).keyup(function() {
            if ($(this).val().toLowerCase() == 'delete') {
                $('#confirm_delete_button').prop('disabled', false);
            } else {
                $('#confirm_delete_button').prop('disabled', true);
            }
        });

        // Close the submit modal when the escape key is pressed
        $(document).on('keydown',function(event) {
            if (event.keyCode == 27) {
                $('#delete-modal').css({ 'display': "none" });
                }
            });

        // Close the submit modal when clicking outside of the window
        $(window).on('click', function(event) {
            if (event.target == $('#delete-modal').get()[0]) {
                $('#delete-modal').css({ 'display': "none" });
            }
        });

        // Allow the submission of a different form when clicking enter
        $('#delete-modal').keypress(function(e) {
            if ((e.keyCode == 13) && ($( "#validate_delete" ).val().toLowerCase() == 'delete')) {
                $('#confirm_delete_button').click();
                return false;
            }
        });
    });

    function show_delete_modal() {
        $('#delete-modal').css({ 'display': 'block' });
        $('#validate_delete').focus();
    };

    // Convert the result from `form.serializeArray()` into something we can
    // iterator over using `$each`.
    function objectify_form(formArray) {

        var returnArray = {};
        for (var i = 0; i < formArray.length; i++){
          returnArray[formArray[i]['name']] = formArray[i]['value'];
        }
        return returnArray;
    }

    // Post a new form to a URL with the specified parameters.
    function my_post(path, parameters) {
        var form = $('<form></form>');

        form.attr("method", "post");
        form.attr("action", path);

        $.each(parameters, function(key, value) {
            var field = $('<input></input>');

            field.attr("type", "hidden");
            field.attr("name", key);
            field.attr("value", value);

            form.append(field);
        });

        // The form needs to be a part of the document in
        // order for us to be able to submit it.
        $(document.body).append(form);
        form.submit();
    }

    function delete_modal_submit() {
        $('#delete_modal_target').prop('value', 'delete');
        var form = $('#delete_modal_target').closest('form');

        // Add the 'validate_delete' so functions can make sure the user entered the text
        form.append("<input type='hidden' id='validate_delete' name='validate_delete' value='delete'>"); 

        // Allow the user to specify a different URL to post the form to as
        // opposed to the default form action.
        var url = $('#delete_modal_target').attr('data-submit-url');
        if (url) {
            my_post(url, objectify_form(form.serializeArray()));
        } else {
            form.submit();
        }
    }
</script>
