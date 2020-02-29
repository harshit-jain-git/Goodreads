(function() {
	var socket = io.connect('http://' + document.domain + ':' + location.port);
	$('.title_search a').on('click',function(){
        q = $('#query_1').val();

        socket.emit('title_search', q);
    });

    $('.author_search a').on('click',function(){
        q = $('#query_2').val();

        socket.emit('author_search', q);
    });

    $('.year_search a').on('click',function(){
        q = $('#query_3').val();
        q = parseFloat(q);
        console.log(q)
        socket.emit('year_search', q);
    });

    $('.tag_search a').on('click',function(){
        q = $('#query_4').val();

        socket.emit('tag_search', q);
    });

    $('.isbn_search a').on('click',function(){
        q = $('#query_5').val();
        q = parseFloat(q);
        socket.emit('isbn_search', q);
    });

    $(document).on('click', '.book_url', function(){
    	title = $(this).text();
    	console.log(title)
    	socket.emit('book_page_request', title);
    });

    socket.on('book_id_result', function(id){
    	window.location = 'http://' + document.domain + ':' + location.port + '/book_page/' + id;
    })

    socket.on('title_search_result', function(rows){
        console.log(rows[0][1]);

    	html = "";
    	for (e of rows) {
    		html = html + '<a class="book_url" href="#">' + e[0] + '</a> &emsp;'
    	}
    	document.getElementById('output').innerHTML = html;
    });

    socket.on('author_search_result', function(rows){
        console.log(rows[0][1]);

    	html = "";
    	for (e of rows) {
    		html = html + '<a class="book_url" href="#">' + e[0] + '</a> &emsp;'
    	}
    	document.getElementById('output').innerHTML = html;
    });

    socket.on('year_search_result', function(rows){
        console.log(rows[0][1]);

    	html = "";
    	for (e of rows) {
    		html = html + '<a class="book_url" href="#">' + e[0] + '</a> &emsp;'
    	}
    	document.getElementById('output').innerHTML = html;
    });

    socket.on('tag_search_result', function(rows){
        console.log(rows[0][1]);

    	html = "";
    	for (e of rows) {
    		html = html + '<a class="book_url" href="#">' + e[0] + '</a> &emsp;'
    	}
    	document.getElementById('output').innerHTML = html;
    });

    socket.on('isbn_search_result', function(rows){
        console.log(rows[0][1]);

    	html = "";
    	for (e of rows) {
    		html = html + '<a class="book_url" href="#">' + e[0] + '</a> &emsp;'
    	}
    	document.getElementById('output').innerHTML = html;
    });

    $(document).on('click', '#best_rated_books', function(){
    	socket.emit('best_rated_books');
    });

    socket.on('best_rated_books_result', function(rows){
    	html = "";
    	for (e of rows) {
    		html = html + '<a class="book_url" href="#">' + e[0] + '</a> &emsp;'
    	}
    	document.getElementById('output').innerHTML = html;
    });

    $(document).on('click', '#best_rated_authors', function(){
    	socket.emit('best_rated_authors');
    });

    socket.on('best_rated_authors_result', function(rows){
    	html = "";
    	for (e of rows) {
    		html = html + '<a class="author_url" href="#">' + e[0] + '</a> &emsp;'
    	}
    	document.getElementById('output').innerHTML = html;
    });

    $(document).on('click', '#most_read_books', function(){
    	socket.emit('most_read_books');
    });

    socket.on('most_read_books_result', function(rows){
    	html = "";
    	for (e of rows) {
    		html = html + '<a class="book_url" href="#">' + e[0] + '</a> &emsp;'
    	}
    	document.getElementById('output').innerHTML = html;
    });

    $(document).on('click', '#most_popular_authors', function(){
    	socket.emit('most_popular_authors');
    });

    socket.on('most_popular_authors_result', function(rows){
    	html = "";
    	for (e of rows) {
    		html = html + '<a class="author_url" href="#">' + e[0] + '</a> &emsp;'
    	}
    	document.getElementById('output').innerHTML = html;
    });

    $(document).on('click', '#most_active_users', function(){
    	socket.emit('most_active_users');
    });

    socket.on('most_active_users_result', function(rows){
    	html = "";
    	for (e of rows) {
    		html = html + '<a class="user_url" href="#">' + e[0] + '</a> &emsp;'
    	}
    	document.getElementById('output').innerHTML = html;
    });

	$(document).on('click', '#most_recent_books', function(){
    	socket.emit('most_recent_books');
    });

    socket.on('most_recent_books_result', function(rows){
    	html = "";
    	for (e of rows) {
    		html = html + '<a class="book_url" href="#">' + e[0] + '</a> &emsp;'
    	}
    	document.getElementById('output').innerHTML = html;
    });    

    $(document).on('click', '#to_read', function(){
    	socket.emit('to_read');
    });

    socket.on('to_read_result', function(rows){
    	html = "";
    	for (e of rows) {
    		html = html + '<a class="book_url" href="#">' + e[0] + '</a> &emsp;'
    	}
    	document.getElementById('output').innerHTML = html;
    });

    $(document).on('click', '#rated_books', function(){
    	socket.emit('rated_books');
    });

    socket.on('rated_books_result', function(rows){
    	html = "";
    	for (e of rows) {
    		html = html + '<a class="book_url" href="#">' + e[0] + '</a> &emsp;'
    	}
    	document.getElementById('output').innerHTML = html;
    });

})(jQuery);