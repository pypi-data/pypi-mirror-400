pub fn try_any<T, E, I, F>(iter: I, mut f: F) -> Result<bool, E>
where
    I: IntoIterator<Item = T>,
    F: FnMut(T) -> Result<bool, E>,
{
    let mut last_err = None;
    for item in iter {
        match f(item) {
            Ok(true) => return Ok(true),
            Ok(false) => continue,
            Err(e) => last_err = Some(e),
        }
    }
    if let Some(e) = last_err {
        Err(e)
    } else {
        Ok(false)
    }
}

pub fn try_all<T, E, I, F>(iter: I, mut f: F) -> Result<bool, E>
where
    I: IntoIterator<Item = T>,
    F: FnMut(T) -> Result<bool, E>,
{
    for item in iter {
        if !f(item)? {
            return Ok(false);
        }
    }
    Ok(true)
}
