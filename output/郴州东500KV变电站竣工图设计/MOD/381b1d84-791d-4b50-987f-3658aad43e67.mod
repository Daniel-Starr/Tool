<?xml version="1.0" encoding="utf-8"?>
<Device>
  <Entities>
    <Entity ID="2" Type="simple" Visible="false">
      <Ring R="30" DR="13" Rad="6.28318530717959" />
      <Color R="255" G="255" B="255" A="0" />
      <TransformMatrix Value="1,0,0,0,0,1,0,0,0,0,1,0,43.4347424026554,5.6843418860808E-15,-13,1" />
    </Entity>
    <Entity ID="3" Type="simple" Visible="false">
      <Cylinder R="13" H="50" />
      <Color R="255" G="255" B="255" A="0" />
      <TransformMatrix Value="0,1,0,0,0,0,1,0,1,0,0,0,78.2929625030582,5.6843418860808E-15,-13,1" />
    </Entity>
    <Entity ID="4" Type="boolean" Visible="true">
      <Boolean Type="Union" Entity1="2" Entity2="3" />
      <Color R="138" G="149" B="151" A="0" />
      <TransformMatrix Value="1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1" />
    </Entity>
    <Entity ID="5" Type="simple" Visible="true">
      <TruncatedCone BR="13" TR="18" H="6" />
      <Color R="138" G="149" B="151" A="0" />
      <TransformMatrix Value="0,1,0,0,0,0,1,0,1,0,0,0,128.292962503058,5.6843418860808E-15,-13,1" />
    </Entity>
  </Entities>
</Device>