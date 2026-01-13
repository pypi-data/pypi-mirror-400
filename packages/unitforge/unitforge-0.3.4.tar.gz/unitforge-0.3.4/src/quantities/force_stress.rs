use crate::impl_macros::macros::*;
use crate::prelude::*;
use ndarray::{Array1, Array2, ArrayView1, ArrayView2};
use num_traits::identities::Zero;
use num_traits::FromPrimitive;
#[cfg(feature = "pyo3")]
use pyo3::pyclass;
#[cfg(feature = "serde")]
use serde::{Deserialize, Serialize};
use std::cmp::Ordering;
use std::fmt;
use std::ops::{Add, AddAssign, Div, DivAssign, Mul, MulAssign, Neg, Sub, SubAssign};
#[cfg(feature = "strum")]
use strum_macros::EnumIter;

#[cfg_attr(feature = "strum", derive(EnumIter))]
#[cfg_attr(feature = "serde", derive(Serialize, Deserialize))]
#[derive(Copy, Clone, PartialEq, Debug)]
#[cfg_attr(feature = "pyo3", pyclass(eq, eq_int))]
pub enum ForceStressUnit {
    Nsq_msq,
}

impl PhysicsUnit for ForceStressUnit {
    fn name(&self) -> &str {
        match &self {
            ForceStressUnit::Nsq_msq => "N^2/m^2",
        }
    }

    fn base_per_x(&self) -> (f64, i32) {
        match self {
            ForceStressUnit::Nsq_msq => (1., 0),
        }
    }
}

impl_quantity!(ForceStress, ForceStressUnit, [ForceStressUnit::Nsq_msq]);
impl_div_with_self_to_f64!(ForceStress);
