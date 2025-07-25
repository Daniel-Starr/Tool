<?xml version="1.0" encoding="utf-8"?>
<Device>
  <Entities>
    <Entity ID="1" Type="simple" Visible="False">
      <Cylinder R="18" H="150" />
      <TransformMatrix Value="1,0,0,0,0,1,0,0,0,0,1,0,1000,199.999999999999,0,1" />
      <Color R="104" G="108" B="94" A="0" />
    </Entity>
    <Entity ID="2" Type="simple" Visible="False">
      <Cylinder R="18" H="150" />
      <TransformMatrix Value="1,0,0,0,0,1,0,0,0,0,1,0,-1000,-200.000000000001,0,1" />
      <Color R="104" G="108" B="94" A="0" />
    </Entity>
    <Entity ID="3" Type="simple" Visible="False">
      <Cylinder R="18" H="150" />
      <TransformMatrix Value="1,0,0,0,0,1,0,0,0,0,1,0,600,199.999999999999,0,1" />
      <Color R="104" G="108" B="94" A="0" />
    </Entity>
    <Entity ID="4" Type="simple" Visible="False">
      <Cylinder R="18" H="150" />
      <TransformMatrix Value="1,0,0,0,0,1,0,0,0,0,1,0,1000,-200.000000000001,0,1" />
      <Color R="104" G="108" B="94" A="0" />
    </Entity>
    <Entity ID="5" Type="simple" Visible="False">
      <Cylinder R="18" H="150" />
      <TransformMatrix Value="1,0,0,0,0,1,0,0,0,0,1,0,600,-200.000000000001,0,1" />
      <Color R="104" G="108" B="94" A="0" />
    </Entity>
    <Entity ID="6" Type="simple" Visible="False">
      <Cylinder R="18" H="150" />
      <TransformMatrix Value="1,0,0,0,0,1,0,0,0,0,1,0,-1000,199.999999999999,0,1" />
      <Color R="104" G="108" B="94" A="0" />
    </Entity>
    <Entity ID="7" Type="simple" Visible="False">
      <Cylinder R="18" H="150" />
      <TransformMatrix Value="1,0,0,0,0,1,0,0,0,0,1,0,-600,199.999999999999,0,1" />
      <Color R="104" G="108" B="94" A="0" />
    </Entity>
    <Entity ID="8" Type="simple" Visible="False">
      <Cylinder R="18" H="150" />
      <TransformMatrix Value="1,0,0,0,0,1,0,0,0,0,1,0,-600,-200.000000000001,0,1" />
      <Color R="104" G="108" B="94" A="0" />
    </Entity>
    <Entity ID="9" Type="simple" Visible="False">
      <Cuboid L="600" W="600" H="150" />
      <TransformMatrix Value="1,0,0,0,0,-1,0,0,0,0,-1,0,-800.000000000002,0,150,1" />
      <Color R="104" G="108" B="94" A="0" />
    </Entity>
    <Entity ID="10" Type="simple" Visible="False">
      <Cuboid L="600" W="600" H="150" />
      <TransformMatrix Value="1,0,0,0,0,-1,0,0,0,0,-1,0,799.999999999998,0,150,1" />
      <Color R="104" G="108" B="94" A="0" />
    </Entity>
    <Entity ID="11" Type="boolean" Visible="False">
      <Boolean Type="Difference" Entity1="9" Entity2="7" />
      <TransformMatrix Value="1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1" />
      <Color R="104" G="108" B="94" A="0" />
    </Entity>
    <Entity ID="12" Type="boolean" Visible="False">
      <Boolean Type="Difference" Entity1="11" Entity2="8" />
      <TransformMatrix Value="1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1" />
      <Color R="104" G="108" B="94" A="0" />
    </Entity>
    <Entity ID="13" Type="boolean" Visible="False">
      <Boolean Type="Difference" Entity1="12" Entity2="6" />
      <TransformMatrix Value="1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1" />
      <Color R="104" G="108" B="94" A="0" />
    </Entity>
    <Entity ID="14" Type="boolean" Visible="True">
      <Boolean Type="Difference" Entity1="13" Entity2="2" />
      <TransformMatrix Value="1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1" />
      <Color R="104" G="108" B="94" A="0" />
    </Entity>
    <Entity ID="15" Type="boolean" Visible="False">
      <Boolean Type="Difference" Entity1="10" Entity2="1" />
      <TransformMatrix Value="1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1" />
      <Color R="104" G="108" B="94" A="0" />
    </Entity>
    <Entity ID="16" Type="boolean" Visible="False">
      <Boolean Type="Difference" Entity1="15" Entity2="4" />
      <TransformMatrix Value="1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1" />
      <Color R="104" G="108" B="94" A="0" />
    </Entity>
    <Entity ID="17" Type="boolean" Visible="False">
      <Boolean Type="Difference" Entity1="16" Entity2="3" />
      <TransformMatrix Value="1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1" />
      <Color R="104" G="108" B="94" A="0" />
    </Entity>
    <Entity ID="18" Type="boolean" Visible="True">
      <Boolean Type="Difference" Entity1="17" Entity2="5" />
      <TransformMatrix Value="1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1" />
      <Color R="104" G="108" B="94" A="0" />
    </Entity>
  </Entities>
</Device>