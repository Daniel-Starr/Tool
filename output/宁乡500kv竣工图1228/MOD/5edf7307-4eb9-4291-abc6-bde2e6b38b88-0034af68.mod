<?xml version="1.0" encoding="utf-8"?>
<Device>
  <Entities>
    <Entity ID="1" Type="simple" Visible="False">
      <Cuboid L="850" W="850" H="150" />
      <TransformMatrix Value="1,0,0,0,0,1,0,0,0,0,1,0,514.280018010178,-501.93729757793,-299.999999999999,1" />
      <Color R="104" G="108" B="94" A="0" />
    </Entity>
    <Entity ID="2" Type="simple" Visible="False">
      <Cuboid L="600" W="600" H="150" />
      <TransformMatrix Value="1,0,0,0,0,1,0,0,0,0,1,0,0,0,-150,1" />
      <Color R="80" G="80" B="80" A="0" />
    </Entity>
    <Entity ID="3" Type="simple" Visible="False">
      <Cylinder R="15" H="600" />
      <TransformMatrix Value="1,0,0,0,0,-1,0,0,0,0,-1,0,-240,240,0,1" />
      <Color R="80" G="80" B="80" A="0" />
    </Entity>
    <Entity ID="4" Type="simple" Visible="False">
      <Cylinder R="15" H="600" />
      <TransformMatrix Value="1,0,0,0,0,-1,0,0,0,0,-1,0,-240,-240,0,1" />
      <Color R="80" G="80" B="80" A="0" />
    </Entity>
    <Entity ID="5" Type="simple" Visible="False">
      <Cylinder R="15" H="600" />
      <TransformMatrix Value="1,0,0,0,0,-1,0,0,0,0,-1,0,240,-240,0,1" />
      <Color R="80" G="80" B="80" A="0" />
    </Entity>
    <Entity ID="6" Type="simple" Visible="False">
      <Cylinder R="15" H="600" />
      <TransformMatrix Value="1,0,0,0,0,-1,0,0,0,0,-1,0,240.000000000001,240,0,1" />
      <Color R="80" G="80" B="80" A="0" />
    </Entity>
    <Entity ID="7" Type="boolean" Visible="False">
      <Boolean Type="Difference" Entity1="2" Entity2="5" />
      <TransformMatrix Value="1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1" />
      <Color R="104" G="108" B="94" A="0" />
    </Entity>
    <Entity ID="8" Type="boolean" Visible="False">
      <Boolean Type="Difference" Entity1="7" Entity2="4" />
      <TransformMatrix Value="1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1" />
      <Color R="104" G="108" B="94" A="0" />
    </Entity>
    <Entity ID="9" Type="boolean" Visible="False">
      <Boolean Type="Difference" Entity1="8" Entity2="6" />
      <TransformMatrix Value="1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1" />
      <Color R="104" G="108" B="94" A="0" />
    </Entity>
    <Entity ID="10" Type="boolean" Visible="True">
      <Boolean Type="Difference" Entity1="9" Entity2="3" />
      <TransformMatrix Value="1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1" />
      <Color R="104" G="108" B="94" A="0" />
    </Entity>
  </Entities>
</Device>