(function(){
	var socket = io.connect('http://' + document.domain + ':' + location.port);
	socket.emit('get_tag_names');

	socket.on('tag_names', function(tags){
		html = "";
		for (e of tags){
			html += '<a href="#">' + e[0] + '</a> &emsp; '
		}

		document.getElementById('tag_names').innerHTML = html;
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


        socket.emit('author_search', q);
    });
})(jQuery);