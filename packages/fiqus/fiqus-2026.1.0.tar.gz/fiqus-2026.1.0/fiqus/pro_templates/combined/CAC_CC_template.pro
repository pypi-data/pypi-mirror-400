Group {
    // Volumes (surfaces in 2D)
    HTS         = Region[{<< rm.powered.HTS.vol.numbers | join(', ') >>}];
    {% set ps_names = rm.induced.Stabilizer.vol.names or [] %}
    {% set ps_nums  = rm.induced.Stabilizer.vol.numbers or [] %}
    Copper      = Region[{<< ps_nums[ ps_names.index('CopperTop') ] >>, << ps_nums[ ps_names.index('CopperBottom') ] >>, << ps_nums[ ps_names.index('CopperLeft') ] >>, << ps_nums[ ps_names.index('CopperRight') ] >>}];
    Silver      = Region[{<< ps_nums[ ps_names.index('SilverTop') ] >>, << ps_nums[ ps_names.index('SilverBottom') ] >>}];
    Substrate   = Region[{<< ps_nums[ ps_names.index('Substrate') ] >>}];
    Air         = Region[<< rm.air.vol.number >>];
    // Surfaces (curves in 2D)
    Air_out     = Region[<< rm.air.surf.number >>];
    Air_in      = Region[<< rm.air.line.number >>];
    // Cuts
    Cut = Region[<< rm.air.cochain.numbers[0] >>];
    // Cut = Region[{}];
    Cuts = Region[{ Cut }];
    // Gauging points
    Gauging_point = Region[{<< rm.air.point.numbers[0] >>}];
    // Abstract domains
    LinOmegaC    = Region[{ Copper, Silver, Substrate }];
    NonLinOmegaC = Region[{ HTS }];
    OmegaC       = Region[{ LinOmegaC, NonLinOmegaC }];
    OmegaCC      = Region[{ Air }];  
    Omega        = Region[{ OmegaC, OmegaCC }];      
    BndOmegaC    = Region[{ Air_in }];
}

Function {
    // ------- GENERAL PARAMETERS -------
    T[] = <<dm.magnet.solve.general_parameters.temperature>>;

    // ------- MATERIAL PARAMETERS -------
    mu0 = Pi*4e-7; // [H/m]
    nu0 = 1.0/mu0; // [m/H]
    mu[Omega] = mu0;
    nu[Omega] = nu0;
    // Normal resistivities
    {% if dm.conductors[dm.magnet.solve.conductor_name].strand.rho_material_stabilizer == 'CFUN_rhoCu' %}
    rho[Copper] = CFUN_rhoCu_T_B[T[], $1]{<<dm.conductors[dm.magnet.solve.conductor_name].strand.RRR>>}; // [Ohm*m]
    {% endif %}
    {% if dm.conductors[dm.magnet.solve.conductor_name].strand.rho_material_silver == 'CFUN_rhoAg' %}
    rho[Silver] = CFUN_rhoAg_T_B[T[], $1]{<<dm.conductors[dm.magnet.solve.conductor_name].strand.RRR_silver>>, 273}; // [Ohm*m]
    {% endif %}
    {% if dm.conductors[dm.magnet.solve.conductor_name].strand.rho_material_substrate == 'CFUN_rhoHast' %}
    rho[Substrate] = CFUN_rhoHast_T[T[]]; // [Ohm*m]
    {% endif %}
    // Power law
    {% if dm.conductors[dm.magnet.solve.conductor_name].Jc_fit.type == 'Succi_fixed' %}
    jc[] = <<dm.conductors[dm.magnet.solve.conductor_name].Jc_fit.Jc_factor>> * CFUN_HTS_JcFit_Succi_T_B[T[], $1];
    {% elif dm.conductors[dm.magnet.solve.conductor_name].Jc_fit.type == 'Fujikura' %}
    jc[] = <<dm.conductors[dm.magnet.solve.conductor_name].Jc_fit.Jc_factor>> * CFUN_HTS_JcFit_Fujikura_T_B_theta[T[], $1, $2];
    {% endif %}
    ec = <<dm.conductors[dm.magnet.solve.conductor_name].strand.ec_superconductor>>;
    n = <<dm.conductors[dm.magnet.solve.conductor_name].strand.n_value_superconductor>>; // [-] power law index, one key parameter for the power law
    eps_jc[] = <<dm.conductors[dm.magnet.solve.conductor_name].strand.minimum_jc_fraction>> * jc[<<dm.conductors[dm.magnet.solve.conductor_name].strand.minimum_jc_field>>, 0.0];
    rho_power[] = ec / (Max[jc[$2, $3],eps_jc[]]) * (Norm[$1] / (Max[jc[$2, $3],eps_jc[]]))^(n - 1); // [Ohm m] power law resistivity
    e_power[] = rho_power[$1, $2, $3] * $1;
    dedj_power[] = (
        ec / ((Max[jc[$2, $3],eps_jc[]])#1) * (Norm[$1]/#1)^(n - 1) * TensorDiag[1, 1, 1] +
        ec / (#1)^3 * (n - 1) * (Norm[$1]/#1)^(n - 3) * SquDyadicProduct[$1]);
    rho[HTS] = rho_power[$1, $2, $3];
    dedj[HTS] = dedj_power[$1, $2, $3];

    angle[] = 180/Pi * Atan2[CompX[$1], CompY[$1]]; // angle of vector with respect to the normal direction in degree (assuming the tape normal is along the y-axis)

    // ------- SOURCE PARAMETERS -------
    directionApplied[] = Vector[Sin[<<dm.magnet.solve.source_parameters.field_angle_with_respect_to_normal_direction>>*Pi/180], Cos[<<dm.magnet.solve.source_parameters.field_angle_with_respect_to_normal_direction>>*Pi/180], 0.];
    {% if dm.magnet.solve.source_parameters.source_type == 'sine' %} 
    // Sine wave source (with DC component)
    f = <<dm.magnet.solve.source_parameters.sine.frequency>>; // Frequency of applied field [Hz]    
    time_multiplier = 1; // Set to 1, as it is being used in the resolution
    I_transport[] =  <<dm.magnet.solve.source_parameters.sine.current_amplitude>> * Sin[2*Pi*f * $Time];   
    hsVal[] = nu0 * (<<dm.magnet.solve.source_parameters.sine.field_amplitude>> * Sin[2*Pi*f * $Time]) * directionApplied[];
    hsVal_prev[] = nu0 *(<<dm.magnet.solve.source_parameters.sine.field_amplitude>> * Sin[2*Pi*f * ($Time-$DTime)]) * directionApplied[];
    {% elif dm.magnet.solve.source_parameters.source_type == 'piecewise' %}
    time_multiplier = <<dm.magnet.solve.source_parameters.piecewise.time_multiplier>>;
    applied_field_multiplier = <<dm.magnet.solve.source_parameters.piecewise.applied_field_multiplier>>;
    transport_current_multiplier = <<dm.magnet.solve.source_parameters.piecewise.transport_current_multiplier>>;
    {% if dm.magnet.solve.source_parameters.piecewise.source_csv_file %} // Source from CSV file
    timeList() = {<<ed['time']|join(', ')>>};
    bList() = {<<ed['b']|join(', ')>>};
    IList() = {<<ed['I']|join(', ')>>};
    timebList() = ListAlt[timeList(), bList()];
    timeIList() = ListAlt[timeList(), IList()];
    hsVal[] = nu0 * applied_field_multiplier * InterpolationLinear[Max[0,($Time)/time_multiplier]]{List[timebList()]} * directionApplied[];
    hsVal_prev[] = nu0 * applied_field_multiplier * InterpolationLinear[Max[0,($Time-$DTime)/time_multiplier]]{List[timebList()]} * directionApplied[];
    I_transport[] = transport_current_multiplier * InterpolationLinear[Max[0,($Time)/time_multiplier]]{List[timeIList()]};
    {% else %} // Source from parameters given as lists
    times_source_piecewise_linear() = {<<dm.magnet.solve.source_parameters.piecewise.times|join(', ')>>};
    transport_currents_relative_piecewise_linear() = {<<dm.magnet.solve.source_parameters.piecewise.transport_currents_relative|join(', ')>>};
    applied_fields_relative_piecewise_linear() = {<<dm.magnet.solve.source_parameters.piecewise.applied_fields_relative|join(', ')>>};
    hsVal[] = nu0 * applied_field_multiplier * InterpolationLinear[Max[0,($Time)/time_multiplier]]{ListAlt[times_source_piecewise_linear(), applied_fields_relative_piecewise_linear()]} * directionApplied[];
    hsVal_prev[] = nu0 * applied_field_multiplier * InterpolationLinear[Max[0,($Time-$DTime)/time_multiplier]]{ListAlt[times_source_piecewise_linear(), applied_fields_relative_piecewise_linear()]} * directionApplied[];
    I_transport[] = transport_current_multiplier * InterpolationLinear[Max[0,($Time)/time_multiplier]]{ListAlt[times_source_piecewise_linear(), transport_currents_relative_piecewise_linear()]};
    {% endif %}
    {% endif %}
    dbsdt[] = mu0 * (hsVal[] - hsVal_prev[]) / $DTime; // must be a finite difference to avoid error accumulation

    // ------- NUMERICAL PARAMETERS -------
    timeStart = 0.; // Initial time [s]
    {% if dm.magnet.solve.source_parameters.source_type == 'sine'%}
        timeFinal = <<dm.magnet.solve.numerical_parameters.sine.number_of_periods_to_simulate>>/f; // Final time for source definition (s)
        dt = 1 / (f*<<dm.magnet.solve.numerical_parameters.sine.timesteps_per_period>>); // Time step (initial if adaptive) (s)
        dt_max = dt; // Fixed maximum time step
        dt_max_var[] = dt_max;
    {% else %}
        timeFinal = <<dm.magnet.solve.numerical_parameters.piecewise.time_to_simulate>>;
        {% if dm.magnet.solve.numerical_parameters.piecewise.variable_max_timestep %}
            times_max_timestep_piecewise_linear() = {<<dm.magnet.solve.numerical_parameters.piecewise.times_max_timestep_piecewise_linear|join(', ')>>};
            max_timestep_piecewise_linear() = {<<dm.magnet.solve.numerical_parameters.piecewise.max_timestep_piecewise_linear|join(', ')>>};
            dt = max_timestep_piecewise_linear(0);
            dt_max_var[] = InterpolationLinear[Max[0,$Time]]{ListAlt[times_max_timestep_piecewise_linear(), max_timestep_piecewise_linear()]};
        {% else %}
            dt = timeFinal / <<dm.magnet.solve.numerical_parameters.piecewise.timesteps_per_time_to_simulate>>;
            dt_max = dt; // Fixed maximum time step
            dt_max_var[] = dt_max;
        {% endif %}
        {% if dm.magnet.solve.numerical_parameters.piecewise.force_stepping_at_times_piecewise_linear%}
            control_time_instants_list() = {<<dm.magnet.solve.source_parameters.piecewise.times|join(', ')>>, 1e99}; // last one is just to avoid 'seg. fault' errors
        {% endif %}
    {% endif %}
    iter_max = 60; // Maximum number of iterations (after which we exit the iterative loop)
    extrapolationOrder = 1; // Extrapolation order for predictor
    tol_energy = <<dm.magnet.solve.numerical_parameters.relative_tolerance>>; // Tolerance on the relative change of the power indicator

    // ------- SIMULATION NAME -------
    name = "txt_files";
    resDirectory = StrCat["./",name];
    infoResidualFile = StrCat[resDirectory,"/residual.txt"];
    outputPower = StrCat[resDirectory,"/power.txt"]; // File updated during runtime
    crashReportFile = StrCat[resDirectory,"/crash_report.txt"];
    outputTemperature = StrCat[resDirectory,"/temperature.txt"];

    {% if dm.magnet.solve.initial_conditions.init_type == 'pos_file' %}
    h_from_file[] = VectorField[XYZ[]]; // After GmshRead[] in Resolution, this vector field contains the solution from a .pos file that can be accessed at any point XYZ[]
    {% endif %}
}

Constraint {
    { Name phi ;
        Case {
            {Region Gauging_point ; Value 0.0 ;}
            {% if dm.magnet.solve.initial_conditions.init_type != 'virgin' %}
            {Region Omega ; Type InitFromResolution ; NameOfResolution Projection_h_to_h ;}
            {% endif %}
        }
    }
    { Name Current ;
        Case {
            {Region Cut ; Type Assign ; Value 1.0 ; TimeFunction I_transport[] ;}
            {% if dm.magnet.solve.initial_conditions.init_type != 'virgin' %}
            {Region Cuts ; Type InitFromResolution ; NameOfResolution Projection_h_to_h ;}
            {% endif %}
        }
    }
    { Name h ; Type Assign ;
        Case {
            {% if dm.magnet.solve.initial_conditions.init_type != 'virgin' %}
            {Region OmegaC ; Type InitFromResolution ; NameOfResolution Projection_h_to_h ;}
            {% endif %}
        }
    }
}

FunctionSpace {
    // Function space for magnetic field h in h-conform formulation. Main field for the magnetodynamic problem.
    { Name h_space; Type Form1;
        BasisFunction {
            { Name gradpsin; NameOfCoef phin; Function BF_GradNode;
                Support Region[{OmegaCC, Air_out}]; Entity NodesOf[OmegaCC]; } // Extend support to boundary for surface integration
            { Name gradpsin; NameOfCoef phin2; Function BF_GroupOfEdges;
                Support OmegaC; Entity GroupsOfEdgesOnNodesOf[BndOmegaC]; } // To treat properly the conducting domain boundary
            { Name psie; NameOfCoef he; Function BF_Edge;
                Support OmegaC; Entity EdgesOf[All, Not BndOmegaC]; }
            { Name ci; NameOfCoef Ii; Function BF_GroupOfEdges;
                Support Omega; Entity GroupsOfEdgesOf[Cuts]; }
        }
        GlobalQuantity {
            { Name I ; Type AliasOf        ; NameOfCoef Ii ; }
            { Name V ; Type AssociatedWith ; NameOfCoef Ii ; }
        }
        Constraint {
            { NameOfCoef he; EntityType EdgesOf; NameOfConstraint h; }
            { NameOfCoef phin; EntityType NodesOf; NameOfConstraint phi; }
            { NameOfCoef phin2; EntityType NodesOf; NameOfConstraint phi; }
            { NameOfCoef Ii ; EntityType GroupsOfEdgesOf ; NameOfConstraint Current ; }
        }
    }
}

Jacobian {
    { Name Vol ;
        Case {
            {Region All ; Jacobian Vol ;}
        }
    }
    { Name Sur ;
        Case {
            { Region All ; Jacobian Sur ; }
        }
    }
}

Integration {
    { Name Int ;
        Case {
            { Type Gauss ;
                Case {
                    { GeoElement Point ; NumberOfPoints 1 ; }
                    { GeoElement Line ; NumberOfPoints 3 ; }
                    { GeoElement Triangle ; NumberOfPoints 3 ; }
                    { GeoElement Quadrangle ; NumberOfPoints 4 ; }
                }
            }
        }
    }
}

Formulation{
    // h-formulation
    { Name MagDyn_hphi; Type FemEquation;
        Quantity {
            { Name h; Type Local; NameOfSpace h_space; }
            { Name hp;Type Local; NameOfSpace h_space; } // to avoid auto-symmetrization by GetDP
            { Name I; Type Global; NameOfSpace h_space[I]; }
            { Name V; Type Global; NameOfSpace h_space[V]; }
        }
        Equation {
            // Time derivative of b (NonMagnDomain)
            Galerkin { [ mu[] * Dof{h} / $DTime , {h} ];
                In Omega; Integration Int; Jacobian Vol;  }
            Galerkin { [ - mu[] * {h}[1] / $DTime , {h} ];
                In Omega; Integration Int; Jacobian Vol;  }
            // Induced current (linear OmegaC)
            Galerkin { [ rho[mu0*Norm[{h}]] * Dof{d h} , {d h} ];
                In LinOmegaC; Integration Int; Jacobian Vol;  }
            Galerkin { [ rho[{d h}, mu0*Norm[{h}], angle[mu0*{h}]] * {d h} , {d h} ];
                In NonLinOmegaC; Integration Int; Jacobian Vol;  }
            Galerkin { [ dedj[{d h}, mu0*Norm[{h}], angle[mu0*{h}]] * Dof{d h} , {d hp} ];
                In NonLinOmegaC; Integration Int; Jacobian Vol;  } // For Newton-Raphson method
            Galerkin { [ - dedj[{d h}, mu0*Norm[{h}], angle[mu0*{h}]] * {d h} , {d hp} ];
                In NonLinOmegaC; Integration Int; Jacobian Vol;  } // For Newton-Raphson method
            // Natural boundary condition for normal flux density
            Galerkin { [ - dbsdt[] * Normal[] , {dInv h} ]; 
                In Air_out; Integration Int; Jacobian Sur;  }
            // Global term
            GlobalTerm { [ Dof{V} , {I} ] ; In Cuts ; }
        }
    }
    {% if dm.magnet.solve.initial_conditions.init_type != 'virgin' %}
    // Projection formulation for initial condition
    { Name Projection_h_to_h; Type FemEquation;
        Quantity {
            { Name h; Type Local; NameOfSpace h_space; }
        }
        Equation{
            // For the current formulation, it seems to be accurate enough to project the field directly (and not its curl as an intermediate to reconstruct it).
            // Validity of this to be checked again if we go to different meshes between the initial condition and the following simulation
            Galerkin { [  Dof{h}, {h} ] ;
                In Omega ; Jacobian Vol ; Integration Int ; }
            {% if dm.magnet.solve.initial_conditions.init_type == 'pos_file' %}
            Galerkin { [ - h_from_file[], {h} ] ;
                In Omega ; Jacobian Vol ; Integration Int ; }
            {% elif dm.magnet.solve.initial_conditions.init_type == 'uniform_field' %}
            Galerkin { [ - hsVal[], {h} ] ;
                In Omega ; Jacobian Vol ; Integration Int ; }
            {% endif %}
        }
    }
    {% endif %}
}

Macro RelaxationFactors
    // Initialize by computing the increment Delta_x
    CopySolution[A,'x_New'];
    AddVector[A, 1, 'x_New', -1, 'x_Prev', 'Delta_x'];
    // Initialize parameters for relaxation search
    Evaluate[$mult = 1.5625];
    Evaluate[$relaxFactor = 0.4096 ]; // Initial relaxation factor (under-relaxation)
    Evaluate[$decreasing = 0]; // Start by increasing the initial factor (possibly up to over-relaxation)
    Evaluate[$relaxTestNb = 0];
    Evaluate[$maxRelaxTestNb = 6];
    // Try with the initial relaxation factor (save in x_Opt)
    AddVector[A, 1, 'x_Prev', $relaxFactor, 'Delta_x', 'x_Opt']; Evaluate[$factor_Opt = $relaxFactor];
    CopySolution['x_Opt', A]; Generate[A]; GetResidual[A, $res];
    // Print[{$relaxFactor, $res}, Format "   Initial factor: %g (res: %g)"];
    // Loop until residual does no longer decrease
    Evaluate[$relaxFactor = $mult * $relaxFactor ];
    While[$relaxTestNb < $maxRelaxTestNb]{
        Evaluate[$res_prev = $res];
        AddVector[A, 1, 'x_Prev', $relaxFactor, 'Delta_x', 'x_New'];
        CopySolution['x_New', A]; Generate[A]; GetResidual[A, $res];
        Evaluate[$relaxTestNb = $relaxTestNb + 1];
        // If residual decreases...
        Test[$res < $res_prev]{
            // Print[{$relaxFactor, $res, $res_prev}, Format "   It has decreased with factor: %g (res: %g, previous: %g)"];
            CopySolution[A,'x_Opt']; Evaluate[$factor_Opt = $relaxFactor];
            // Try another relaxation factor
            Test[$decreasing == 0]{
                Evaluate[$relaxFactor = $relaxFactor * $mult];
            }
            {
                Evaluate[$relaxFactor = $relaxFactor / $mult];
            }
        }
        // otherwise...
        {
            // Print[{$relaxFactor, $res, $res_prev}, Format "   It has NOT decreased with factor: %g (res: %g, previous: %g)"];
            // If just starting, decrease the factor instead...
            Test[$relaxTestNb == 1]{
                Evaluate[$decreasing = 1];
                Evaluate[$relaxFactor = $relaxFactor / ($mult*$mult)];
            }
            // otherwise, exit the loop and use the last guess as the optimum
            {
                Break; // Abort the while loop
            }
        }
    }
    CopySolution['x_Opt',A]; // Copy the optimal solution into the system
Return

Macro CustomIterativeLoop
    // Compute first solution guess and residual at step $TimeStep
    Generate[A];
    Solve[A]; Evaluate[ $syscount = $syscount + 1 ];
    Generate[A]; GetResidual[A, $res0];
    Evaluate[ $res = $res0 ];
    Evaluate[ $iter = 0 ];
    Evaluate[ $convCrit = 1e99 ];
    Evaluate[ $factor_Opt = 1 ]; // relaxation factor; 1 by default, might be modified if RelaxationFactors macro is called
    PostOperation[MagDyn_energy];
    Print[{$iter, $res, $res / $res0, $indicLoss},
        Format "%g %14.12e %14.12e %14.12e 1", File infoResidualFile];
    // ----- Enter the iterative loop (hand-made) -----
    While[$convCrit > 1 && $res / $res0 <= 1e10 && $iter < iter_max]{
        {% if dm.magnet.solve.numerical_parameters.relaxation_factors %}
        CopySolution[A,'x_Prev']; // Save previous solution
        {% endif %}
        Solve[A]; Evaluate[ $syscount = $syscount + 1 ];
        {% if dm.magnet.solve.numerical_parameters.relaxation_factors %}
        // If the number of iteration exceeds 10, try to improve the solution further (i.e., reduce the residual); otherwise, just continue
        Test[$iter >= 10]{Call RelaxationFactors;}
        {% endif %}
        Generate[A]; GetResidual[A, $res];
        Evaluate[ $iter = $iter + 1 ];
        Evaluate[ $indicLossOld = $indicLoss];
        PostOperation[MagDyn_energy];
        Print[{$iter, $res, $res / $res0, $indicLoss, $factor_Opt},
            Format "%g %14.12e %14.12e %14.12e %g", File infoResidualFile];
        // Evaluate the convergence indicator
        Evaluate[ $relChangeACLoss = Abs[($indicLossOld - $indicLoss)/((Abs[$indicLossOld]>1e-7 || $iter < 10) ? $indicLossOld:1e-7)] ];
        Evaluate[ $convCrit = $relChangeACLoss/tol_energy];
    }
Return

Resolution {
    { Name MagDyn;
        System {
            {Name A; NameOfFormulation MagDyn_hphi;}
        }
        Operation {
            // Initialize directories
            CreateDirectory[resDirectory];
            DeleteFile[outputPower];
            DeleteFile[infoResidualFile];
            // Initialize the solution (initial condition)
            SetTime[ timeStart ];
            SetDTime[ dt ];
            SetTimeStep[ 0 ];
            InitSolution[A];
            SaveSolution[A]; // Saves the solution x (from Ax = B) to .res file
            Evaluate[ $syscount = 0 ];
            Evaluate[ $saved = 1 ];
            Evaluate[ $elapsedCTI = 1 ]; // Number of control time instants already treated
            Evaluate[ $isCTI = 0 ];
            // ----- Enter implicit Euler time integration loop (hand-made) -----
            // Avoid too close steps at the end. Stop the simulation if the step becomes ridiculously small
            SetExtrapolationOrder[ extrapolationOrder ];
            While[$Time < timeFinal] {
                SetTime[ $Time + $DTime ]; // Time instant at which we are looking for the solution
                SetTimeStep[ $TimeStep + 1 ];
                {% if dm.magnet.solve.numerical_parameters.piecewise.force_stepping_at_times_piecewise_linear and dm.magnet.solve.source_parameters.source_type == 'piecewise'%}
                // Make sure all CTI are exactly chosen
                Evaluate[ $isCTI = 0 ];
                Test[$Time >= time_multiplier*AtIndex[$elapsedCTI]{List[control_time_instants_list]} - 1e-7 ]{
                    Evaluate[ $isCTI = 1, $prevDTime = $DTime ]; // Also save the previous time step to restart from it after the CTI
                    SetDTime[ time_multiplier*AtIndex[$elapsedCTI]{List[control_time_instants_list]} - $Time + $DTime ];
                    SetTime[ time_multiplier*AtIndex[$elapsedCTI]{List[control_time_instants_list]} ]; // To compute exactly at the asked time instant
                    Print[{$Time}, Format "*** Control time instant: %g s."];
                }
                {% endif %}
                // Iterative loop defined as a macro above
                Print[{$Time, $DTime, $TimeStep}, Format "Start new time step. Time: %g s. Time step: %g s. Step: %g."];
                Call CustomIterativeLoop;
                // Has it converged? If yes, save solution and possibly increase the time step...
                Test[ $iter < iter_max && ($res / $res0 <= 1e10 || $res0 == 0)]{
                    Print[{$Time, $DTime, $iter}, Format "Converged time %g s with time step %g s in %g iterations."];
                    // Save the solution of few time steps (small correction to avoid bad rounding)
                    // Test[ $Time >= $saved * writeInterval - 1e-7 || $Time + $DTime >= timeFinal]{
                    // Test[ $Time >= $saved * $DTime - 1e-7 || $Time + $DTime >= timeFinal]{
                    Test[ 1 ]{
                        SaveSolution[A];
                        // post
                        PostOperation[MagDyn_energy];
                        Print[{$Time, $saved}, Format "Saved time %g s (saved solution number %g). Output power infos:"];
                        Print[{$Time, $indicLoss}, Format "%g %14.12e", File outputPower];
                        Evaluate[$saved = $saved + 1];
                    }
                    {% if dm.magnet.solve.numerical_parameters.voltage_per_meter_stopping_criterion %}
                    PostOperation[V];
                    Print[{$voltage}, Format "Voltage per meter: %14.12e V/m"];
                    Test[ Abs[$voltage] >= <<dm.magnet.solve.numerical_parameters.voltage_per_meter_stopping_criterion>>]{
                        Print["Stopping voltage per meter of <<dm.magnet.solve.numerical_parameters.voltage_per_meter_stopping_criterion>> V/m reached. Stopping simulation."];
                        Break; // Abort the time loop
                    }
                    {% endif %}
                    {% if dm.magnet.solve.numerical_parameters.piecewise.force_stepping_at_times_piecewise_linear and dm.magnet.solve.source_parameters.source_type == 'piecewise' %}
                    // Consider the time step before the control time instant (if relevant) and increment $elapsedCTI
                    Test[ $isCTI == 1 ]{
                        Evaluate[ $elapsedCTI = $elapsedCTI + 1 ];
                        SetDTime[ $prevDTime ];
                    }
                    {% endif %}
                    // Increase the step if we converged sufficiently "fast" (and not a control time instant)
                    Test[ $iter < iter_max / 4 && $DTime < dt_max_var[] && $isCTI == 0 ]{
                        Evaluate[ $dt_new = Min[$DTime * 2, dt_max_var[]] ];
                        Print[{$dt_new}, Format "*** Fast convergence: increasing time step to %g"];
                        SetDTime[$dt_new];
                    }
                    Test[ $DTime > dt_max_var[]]{
                        Evaluate[ $dt_new = dt_max_var[] ];
                        Print[{$dt_new}, Format "*** Variable maximum time-stepping: reducing time step to %g"];
                        SetDTime[$dt_new];
                    }
                }
                // ...otherwise, reduce the time step and try again
                {
                    Evaluate[ $dt_new = $DTime / 2 ];
                    Print[{$iter, $dt_new},
                        Format "*** Non convergence (iter %g): recomputing with reduced step %g"];
                    RemoveLastSolution[A];
                    SetTime[$Time - $DTime];
                    SetTimeStep[$TimeStep - 1];
                    SetDTime[$dt_new];
                    // If it gets ridicoulously small, end the simulation, and report the information in crash file.
                    Test[ $dt_new < dt_max_var[]/10000 ]{
                        Print[{$iter, $dt_new, $Time},
                            Format "*** Non convergence (iter %g): time step %g too small, stopping the simulation at time %g s.", File crashReportFile];
                        // Print[A];
                        Exit;
                    }
                }
            } // ----- End time loop -----
            // Print information about the resolution and the nonlinear iterations
            Print[{$syscount}, Format "Total number of linear systems solved: %g"];
        }
    }
    {% if dm.magnet.solve.initial_conditions.init_type != 'virgin' %}
    { Name Projection_h_to_h;
        System {
            {Name Projection_h_to_h; NameOfFormulation Projection_h_to_h; DestinationSystem A ;}
        }
        Operation {
            {% if dm.magnet.solve.initial_conditions.init_type == 'pos_file' %}
            GmshRead[StrCat["../", "Solution_<<dm.magnet.solve.initial_conditions.solution_to_init_from>>/", "last_magnetic_field.pos"]]; // This file has to be in format without mesh (no -v2, here with GmshParsed format)
            {% endif %}
            Generate[Projection_h_to_h]; Solve[Projection_h_to_h];
            TransferSolution[Projection_h_to_h];
        }
    }
    {% endif %}
}

PostProcessing {
    { Name MagDyn_hphi; NameOfFormulation MagDyn_hphi;
        Quantity {
            { Name phi; Value{ Local{ [ {dInv h} ] ;
                In OmegaCC; Jacobian Vol; } } }
            { Name h; Value{ Local{ [ {h} ] ;
                In Omega; Jacobian Vol; } } }
            { Name b; Value{ Local{ [ mu[] * {h} ] ;
                In Omega; Jacobian Vol; } } }
            { Name b_reaction; Value{ Local{ [ mu[] * ({h} - hsVal[]) ] ;
                In Omega; Jacobian Vol; } } }
            { Name j; Value{ Local{ [ {d h} ] ;
                In OmegaC; Jacobian Vol; } } }
            { Name power; Value{ 
                Local{ [rho[mu0*Norm[{h}]] * {d h} * {d h}] ; In LinOmegaC; Jacobian Vol; }
                Local{ [rho[{d h}, mu0*Norm[{h}], angle[mu0*{h}]] * {d h} * {d h}] ; In NonLinOmegaC; Jacobian Vol; } } }
            { Name totalLoss;
                Value{
                    Integral{ [rho[mu0*Norm[{h}]] * {d h} * {d h}] ;
                        In LinOmegaC ; Integration Int ; Jacobian Vol; }
                    Integral{ [rho[{d h}, mu0*Norm[{h}], angle[mu0*{h}]] * {d h} * {d h}] ;
                        In NonLinOmegaC ; Integration Int ; Jacobian Vol; }
                }
            }
            { Name I; Value { Term{ [ {I} ] ; In Cuts; } } }
            { Name V; Value { Term{ [ {V} ] ; In Cuts; } } }
        }
    }
}

PostOperation {   
    { Name MagDyn;
        NameOfPostProcessing MagDyn_hphi;
        Operation {
            {% set units_dict = {
                "b": "T",
                "b_reaction": "T",
                "h": "A/m",
                "phi": "A",
                "j": "A/m2",
                "jz": "A/m2",
                "jc": "A/m2",
                "power": "W/m3",
            } %}
            // Local field solutions
            {% for quantity, region in zip(dm.magnet.postproc.pos_files.quantities, dm.magnet.postproc.pos_files.regions) %}
            Print[ <<quantity>>, OnElementsOf <<region>> , File StrCat["<<quantity>>_<<region>>.pos"], Name "<<quantity>> [<<units_dict[quantity]>>]" ];
            {% endfor %}
            Print[ I, OnRegion Cut, File StrCat[resDirectory,"/I.txt"], Format SimpleTable];
            Print[ V, OnRegion Cut, File StrCat[resDirectory,"/V.txt"], Format SimpleTable];
            // Last magnetic field solution for projection. Always saved. Note the special format GmshParsed required for proper GmshRead[] operation in the later pre-resolution.
            Print[ h, OnElementsOf Omega, Format GmshParsed , File "last_magnetic_field.pos", Name "h [A/m]", LastTimeStepOnly ];
        }
    }

    { Name MagDyn_energy; LastTimeStepOnly 1 ;
        NameOfPostProcessing MagDyn_hphi;
        Operation {
            Print[ totalLoss[OmegaC], OnGlobal, Format Table, StoreInVariable $indicLoss, File StrCat[resDirectory,"/dummy_loss.txt"] ];
        }
    }
    { Name V; LastTimeStepOnly 1 ;
        NameOfPostProcessing MagDyn_hphi;
        Operation {
            Print[ V, OnRegion Cut, Format Table, StoreInVariable $voltage, File StrCat[resDirectory,"/dummy_v.txt"] ];
        }
    }
}
