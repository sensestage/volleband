OSCFunc.trace( false );

OSCdef( \rssi, { |msg| ~rssi = msg[2] }, '/rx/rssi');

//NetAddr.langPort

// from SenseWorld Quark

~plotter = SWPlotterMonitor.new( { [ ~rssi ] }, 100, 1, 0.05, 2 );
~plotter.start;