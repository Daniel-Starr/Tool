<?xml version="1.0" encoding="utf-8"?>
<Device>
  <Entities>
    <Entity ID="2" Type="simple" Visible="true">
      <Cuboid L="50" W="100" H="50" />
      <Color R="138" G="149" B="151" A="0" />
      <TransformMatrix Value="1,0,0,0,0,0,1,0,0,-1,0,0,-307.999999999999,-100,2158.5,1" />
    </Entity>
    <Entity ID="3" Type="simple" Visible="false">
      <Cuboid L="700" W="683" H="200" />
      <Color R="138" G="149" B="151" A="0" />
      <TransformMatrix Value="1,0,0,0,0,0,1,0,0,-1,0,0,-57.999999999999,99.9999999999999,2158.5,1" />
    </Entity>
    <Entity ID="4" Type="simple" Visible="false">
      <Cuboid L="150" W="100" H="20" />
      <Color R="138" G="149" B="151" A="0" />
      <TransformMatrix Value="1,0,0,0,0,1,0,0,0,0,1,0,-57.999999999999,1.4210854715202E-14,1797,1" />
    </Entity>
    <Entity ID="5" Type="simple" Visible="false">
      <Cylinder R="50" H="20" />
      <Color R="138" G="149" B="151" A="0" />
      <TransformMatrix Value="1,0,0,0,0,1,0,0,0,0,1,0,17.000000000001,1.4210854715202E-14,1797,1" />
    </Entity>
    <Entity ID="6" Type="boolean" Visible="false">
      <Boolean Type="Union" Entity1="4" Entity2="5" />
      <Color R="138" G="149" B="151" A="0" />
      <TransformMatrix Value="1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1" />
    </Entity>
    <Entity ID="7" Type="simple" Visible="false">
      <Cylinder R="50" H="20" />
      <Color R="138" G="149" B="151" A="0" />
      <TransformMatrix Value="1,0,0,0,0,1,0,0,0,0,1,0,-132.999999999999,1.4210854715202E-14,1797,1" />
    </Entity>
    <Entity ID="8" Type="boolean" Visible="false">
      <Boolean Type="Union" Entity1="6" Entity2="7" />
      <Color R="138" G="149" B="151" A="0" />
      <TransformMatrix Value="1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1" />
    </Entity>
    <Entity ID="9" Type="boolean" Visible="true">
      <Boolean Type="Union" Entity1="3" Entity2="8" />
      <Color R="138" G="149" B="151" A="0" />
      <TransformMatrix Value="1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1" />
    </Entity>
  </Entities>
</Device>