<?xml version="1.0" encoding="utf-8"?>
<Device>
  <Entities>
    <Entity ID="1" Type="simple" Visible="False">
      <Cylinder R="9" H="10" />
      <TransformMatrix Value="1,0,0,0,0,1,0,0,0,0,1,0,4162.5,3077.5,2730,1" />
      <Color R="138" G="149" B="151" A="0" />
    </Entity>
    <Entity ID="2" Type="simple" Visible="False">
      <Cylinder R="9" H="10" />
      <TransformMatrix Value="1,0,0,0,0,1,0,0,0,0,1,0,3937.5,3077.5,2730,1" />
      <Color R="138" G="149" B="151" A="0" />
    </Entity>
    <Entity ID="3" Type="simple" Visible="False">
      <Cylinder R="9" H="10" />
      <TransformMatrix Value="1,0,0,0,0,1,0,0,0,0,1,0,4162.5,3302.5,2730,1" />
      <Color R="138" G="149" B="151" A="0" />
    </Entity>
    <Entity ID="4" Type="simple" Visible="False">
      <Cylinder R="9" H="10" />
      <TransformMatrix Value="1,0,0,0,0,1,0,0,0,0,1,0,3937.5,3302.5,2730,1" />
      <Color R="138" G="149" B="151" A="0" />
    </Entity>
    <Entity ID="5" Type="simple" Visible="False">
      <Cuboid L="300" W="300" H="10" />
      <TransformMatrix Value="1,0,0,0,0,1,0,0,0,0,1,0,4050,3190,2730,1" />
      <Color R="138" G="149" B="151" A="0" />
    </Entity>
    <Entity ID="6" Type="simple" Visible="True">
      <Cylinder R="100" H="50" />
      <TransformMatrix Value="1,0,0,0,0,1,0,0,0,0,1,0,4050,3190,2740,1" />
      <Color R="138" G="149" B="151" A="0" />
    </Entity>
    <Entity ID="7" Type="simple" Visible="True">
      <PorcelainBushing H="500" R="90" R1="150" R2="112.5" N="15" />
      <TransformMatrix Value="1,0,0,0,0,1,0,0,0,0,1,0,4050,3190,2790,1" />
      <Color R="91" G="58" B="41" A="0" />
    </Entity>
    <Entity ID="8" Type="simple" Visible="True">
      <TruncatedCone BR="80" TR="100" H="50" />
      <TransformMatrix Value="1,0,0,0,0,1,0,0,0,0,1,0,4050,3190,3290,1" />
      <Color R="138" G="149" B="151" A="0" />
    </Entity>
    <Entity ID="9" Type="boolean" Visible="False">
      <Boolean Type="Difference" Entity1="5" Entity2="3" />
      <TransformMatrix Value="1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1" />
      <Color R="138" G="149" B="151" A="0" />
    </Entity>
    <Entity ID="10" Type="boolean" Visible="False">
      <Boolean Type="Difference" Entity1="9" Entity2="4" />
      <TransformMatrix Value="1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1" />
      <Color R="138" G="149" B="151" A="0" />
    </Entity>
    <Entity ID="11" Type="boolean" Visible="False">
      <Boolean Type="Difference" Entity1="10" Entity2="1" />
      <TransformMatrix Value="1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1" />
      <Color R="138" G="149" B="151" A="0" />
    </Entity>
    <Entity ID="12" Type="boolean" Visible="True">
      <Boolean Type="Difference" Entity1="11" Entity2="2" />
      <TransformMatrix Value="1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1" />
      <Color R="138" G="149" B="151" A="0" />
    </Entity>
  </Entities>
</Device>