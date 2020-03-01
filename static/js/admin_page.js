(function(){
	var socket = io.connect('http://' + document.domain + ':' + location.port);
	$.getScript("https://cdnjs.cloudflare.com/ajax/libs/bootbox.js/5.4.0/bootbox.min.js");
	socket.emit('get_tag_names');

	socket.on('tag_names', function(tags){
		html = "";
		for (e of tags){
			html += '<a href="#">' + e[0] + '</a> &emsp; '
		}

		document.getElementById('tag_names').innerHTML = html;
	});

	socket.on('book_request_result', function(flag){
		var str = "";
		console.log(flag);
		if(flag){
			str = "Book added successfully";
		}
		else {
			str = "Provide valid input";
		}
		console.log(str);
        bootbox.alert(str);
	});

	$('#add_book_button').on('click',function(){
        title = $('#title').val();
		goodreads_book_id = $('#goodreads_book_id').val();
		isbn = $('#isbn').val();
		isbn13 = $('#isbn13').val();
		authors = $('#authors').val();
		original_publication_year = $('#original_publication_year').val();
		language = $('#language').val();
		image_url = $('#image_url').val();

		var q = {
			'title' : title,
			'goodreads_book_id' : goodreads_book_id,
			'isbn' : isbn,
			'isbn13' : isbn13,
			'authors' : authors,
			'original_publication_year' : original_publication_year,
			'language' : language,
			'image_url' : image_url
		};

        socket.emit('add_book_request', q);
    });

    $('#add_tag_button').on('click',function(){
    	goodreads_book_id = $('#goodreads_book_id_tag').val();
		tag_name = $('#tag').val();
		var q = {
			'goodreads_book_id' : goodreads_book_id,
			'tag_name' : tag_name
		};
		console.log("yo");
        socket.emit('add_tag_request', q);
    });

    socket.on('tag_added', function(){
    	bootbox.alert("Tag added successfully!");
    });

    $(document).on('click', '#logout', function(){
        console.log("logout request");
        socket.emit('logout_request');
    });

    socket.on('logged_out', function(){
        bootbox.alert("Logged out successfully!");
        setTimeout(function(){
            window.location = 'http://' + document.domain + ':' + location.port + '/';
        }, 3000);
    });

})(jQuery);