(function () {
    "use strict";
    var socket = io.connect('http://' + document.domain + ':' + location.port);
    var camera = false;
    window.onload = function() {
		console.log('opening presentation');
		socket.emit('open presentation');
	}
    
    document.addEventListener('keydown', (event) => {
      const keyName = event.key;
      if (keyName == 'ArrowDown' || keyName == 'ArrowRight') {
        console.log('keydown event\n' + 'key: ' + keyName);
        socket.emit('nextSlide');
      } else if (keyName == 'ArrowUp' || keyName == 'ArrowLeft') {
        console.log('keydown event\n' + 'key: ' + keyName);
        socket.emit('previousSlide');
      } else if (keyName == 'Esc') {
        socket.emit('close_ppt');
      } else if (keyName == 'C' || keyName == 'c') {
        if (!camera) {
          socket.emit('start_camera');
          camera = true;
        } else {
          camera = false;
          socket.emit('stop_camera');
        }
      } else if (keyName == 'b' || keyName == 'B') {
        console.log('keydown event\n' + 'key: ' + keyName);
        socket.emit('blank');
      }
    });

    setTimeout(function() {
        $(".page-message").fadeOut(500);
    }, 1000);

    $(".submit-button button").click(function () {
      console.log('apply button clicked')
      $(".message").fadeIn("slow");
      $(".message").fadeOut(1000);
      if($("#Radio1").is(':checked')) {
        socket.emit('applyChanges', 1)
      } else if ($("#Radio2").is(':checked')) {
        socket.emit('applyChanges', 2)
      } else socket.emit('applyChanges', 3)
    });
    
    window.onbeforeunload = function (event) {
		socket.emit('close_ppt');
  };
  
  document.addEventListener('touchstart', handleTouchStart, false);        
  document.addEventListener('touchmove', handleTouchMove, false);

  var xDown = null;                                                        
  var yDown = null;                                                        

  function handleTouchStart(evt) {                                         
    xDown = evt.touches[0].clientX;                                      
    yDown = evt.touches[0].clientY;                                      
  };                                                

  function handleTouchMove(evt) {
    if ( ! xDown || ! yDown ) {
        return;
    }

    var xUp = evt.touches[0].clientX;                                    
    var yUp = evt.touches[0].clientY;

    var xDiff = xDown - xUp;
    var yDiff = yDown - yUp;

    if ( Math.abs( xDiff ) > Math.abs( yDiff ) ) {/*most significant*/
      if ( xDiff > 0 ) {
          /* left swipe */ 
          console.log('keydown event\n' + 'key: ' + keyName);
          socket.emit('previousSlide');
      } else {
          /* right swipe */
          console.log('keydown event\n' + 'key: ' + keyName);
          socket.emit('nextSlide');
      }                       
    }
    /* reset values */
    xDown = null;
    yDown = null;                                             
  };

})(jQuery);
