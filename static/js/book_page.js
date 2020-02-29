(function() {
	var socket = io.connect('http://' + document.domain + ':' + location.port);
    var x = document.URL;
    x = x.split('/');
    var id = x[x.length - 1];
    id = id.replace('#', '');
    var rating;
    var to_read;

    $(document).on('click', '#to_read_0', function(){
        if (to_read == 0){}
        else {
            socket.emit('update_to_read', id, 0);
        }
    });

    $(document).on('click', '#to_read_1', function(){
        if (to_read == 1){}
        else {
            socket.emit('update_to_read', id, 1);
        }
    });

    $(document).on('click', '#rating_id_1', function(){
        flag = 0;
        if (rating == -1)
            flag = 1;
        if (rating == 1) {}
        else {
            socket.emit('update_rating', id, 1, flag);
        }
    });
    $(document).on('click', '#rating_id_2', function(){
        flag = 0;
        if (rating == -1)
            flag = 1;
        if (rating == 2) {}
        else {
            socket.emit('update_rating', id, 2, flag);
        }
    });
    $(document).on('click', '#rating_id_3', function(){
        flag = 0;
        if (rating == -1)
            flag = 1;
        if (rating == 3) {}
        else {
            socket.emit('update_rating', id, 3, flag);
        }
    });
    $(document).on('click', '#rating_id_4', function(){
        flag = 0;
        if (rating == -1)
            flag = 1;
        if (rating == 4) {}
        else {
            socket.emit('update_rating', id, 4, flag);
        }
    });
    $(document).on('click', '#rating_id_5', function(){
        flag = 0;
        if (rating == -1)
            flag = 1;
        if (rating == 5) {}
        else {
            socket.emit('update_rating', id, 5, flag);
        }
    });
    $(document).on('click', '#unrate', function(){
        if (rating == -1) {}
        else {
            socket.emit('update_rating', id, rating, 2);
        }
    });

    socket.emit('get_book_details', id);

    socket.on('post_rating_update', function(){
        console.log("Rating updated");
        location.reload(true);
    });

    socket.on('post_to_read_update', function(){
        console.log("To read updated");
        location.reload(true);
    });

    socket.on('book_details', function(rows){
        $('#url').attr('src', rows[12]);

        var text = $('#book_title').text();
        text += rows[0];
        $('#book_title').text(text);

        var text = $('#book_author').text();
        text += rows[1];
        $('#book_author').text(text);

        var text = $('#book_year').text();
        text += rows[2];
        $('#book_year').text(text);

        var text = $('#book_isbn').text();
        text += rows[3];
        $('#book_isbn').text(text);

        var text = $('#book_lang').text();
        text += rows[4];
        $('#book_lang').text(text);

        var text = $('#book_rating').text();
        text += rows[5];
        $('#book_rating').text(text);

        var text = $('#book_rating_count').text();
        text += rows[6];
        $('#book_rating_count').text(text);

        var text = $('#book_ratings_1').text();
        text += rows[7];
        $('#book_ratings_1').text(text);

        var text = $('#book_ratings_2').text();
        text += rows[8];
        $('#book_ratings_2').text(text);

        var text = $('#book_ratings_3').text();
        text += rows[9];
        $('#book_ratings_3').text(text);

        var text = $('#book_ratings_4').text();
        text += rows[10];
        $('#book_ratings_4').text(text);

        var text = $('#book_ratings_5').text();
        text += rows[11];
        $('#book_ratings_5').text(text);

        tags = rows[14];
        console.log(tags);
        var text = $('#book_tags').text();
        for (x of tags){
            text += x + ' | '; 
        }

        $('#book_tags').text(text);

        rating = rows[15];
        if (rows[15] != -1) {
            var aid = "#rating_id_" + rows[15];
            $(aid).css("background-color","yellow");
        }
        else {
            $('#unrate').css("background-color","yellow");
        }

        to_read = rows[16];
        console.log(to_read);
        var aid = "#to_read_" + rows[16];
        $(aid).css("background-color","yellow");

    });


	

})(jQuery);