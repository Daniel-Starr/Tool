<?xml version="1.0" encoding="utf-8"?>
<Device>
  <Entities>
    <Entity ID="2" Type="simple" Visible="false">
      <Cuboid L="400" W="400" H="10" />
      <Color R="138" G="149" B="151" A="0" />
      <TransformMatrix Value="1,0,0,0,0,1,0,0,0,0,1,0,4.44089209850063E-15,1.75804013221841,5000,1" />
    </Entity>
    <Entity ID="3" Type="simple" Visible="false">
      <Cylinder R="12" H="10" />
      <Color R="138" G="149" B="151" A="0" />
      <TransformMatrix Value="1,0,0,0,0,1,0,0,0,0,1,0,175,176.758040132219,5000,1" />
    </Entity>
    <Entity ID="4" Type="boolean" Visible="false">
      <Boolean Type="Difference" Entity1="2" Entity2="3" />
      <Color R="255" G="255" B="255" A="0" />
      <TransformMatrix Value="1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1" />
    </Entity>
    <Entity ID="5" Type="simple" Visible="false">
      <Cylinder R="12" H="10" />
      <Color R="138" G="149" B="151" A="0" />
      <TransformMatrix Value="1,0,0,0,0,1,0,0,0,0,1,0,175,-173.241959867781,5000,1" />
    </Entity>
    <Entity ID="6" Type="boolean" Visible="false">
      <Boolean Type="Difference" Entity1="4" Entity2="5" />
      <Color R="255" G="255" B="255" A="0" />
      <TransformMatrix Value="1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1" />
    </Entity>
    <Entity ID="7" Type="simple" Visible="false">
      <Cylinder R="12" H="10" />
      <Color R="138" G="149" B="151" A="0" />
      <TransformMatrix Value="1,0,0,0,0,1,0,0,0,0,1,0,-175,176.758040132219,5000,1" />
    </Entity>
    <Entity ID="8" Type="boolean" Visible="false">
      <Boolean Type="Difference" Entity1="6" Entity2="7" />
      <Color R="255" G="255" B="255" A="0" />
      <TransformMatrix Value="1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1" />
    </Entity>
    <Entity ID="9" Type="simple" Visible="false">
      <Cylinder R="12" H="10" />
      <Color R="138" G="149" B="151" A="0" />
      <TransformMatrix Value="1,0,0,0,0,1,0,0,0,0,1,0,-175,-173.241959867781,5000,1" />
    </Entity>
    <Entity ID="10" Type="boolean" Visible="true">
      <Boolean Type="Difference" Entity1="8" Entity2="9" />
      <Color R="231" G="235" B="218" A="0" />
      <TransformMatrix Value="6.12323399573677E-17,1,0,0,-1,6.12323399573677E-17,0,0,0,0,1,0,0,0,0,1" />
    </Entity>
    <Entity ID="11" Type="simple" Visible="true">
      <Cylinder R="150" H="5000" />
      <Color R="231" G="235" B="218" A="0" />
      <TransformMatrix Value="6.12323399573677E-17,1,0,0,-1,6.12323399573677E-17,0,0,0,0,1,0,0,0,0,1" />
    </Entity>
  </Entities>
</Device>