//OSCFunc.trace( false );

// varieer 50 voor het aantal samples om over te middelen:
~rssimid = List.fill( 50, {0} );

OSCdef( \rssi, { |msg| ~rssi = msg[2].postln; ~rssimid = ~rssimid.put(0, msg[2] ).rotate(1); }, '/rx/rssi');
//OSCdef( \rssi, { |msg| ~rssi = msg[2].postln; }, '/rx/rssi');

OSCdef( \rssiNdef, { |msg| Ndef(\noisysonify ).set( \midi, ~rssimid.sum/50 ) }, '/rx/rssi');

// from SenseWorld Quark

~plotter = SWPlotterMonitor.new( { [ ~rssi ] }, 100, 1, 0.05, 2 );
~plotter.start;

~plotterMID = SWPlotterMonitor.new( { [ ~rssimid.sum ] }, 100, 1, 0.05, 2 );
~plotterMID.start;


mean = RunningSum.kr( input, length )/length;


s.boot;

Ndef( \noisysonify, { Resonz.ar( Saw.ar( \midi.kr(40).midicps.lag(0.1), 0.2 ), \midi.kr(40).midicps.lag(0.1) * [1,1.5,2,3,5,7,9,11], 0.2 ).sum } );
Ndef( \noisysonify ).play;

NdefMixer.new(s);

